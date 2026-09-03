import { GoogleGenAI } from "@google/genai";

let aiClient: GoogleGenAI | null = null;
let apiCooldownUntil = 0;

function getGenAI(): GoogleGenAI | null {
  if (Date.now() < apiCooldownUntil) {
    return null; // In cooldown due to rate-limiting / quota
  }
  if (!aiClient && process.env.GEMINI_API_KEY) {
    aiClient = new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        },
      },
    });
  }
  return aiClient;
}

function handleGeminiError(error: any) {
  const errMsg = String(error?.message || error || '');
  if (errMsg.includes('429') || errMsg.includes('RESOURCE_EXHAUSTED') || errMsg.includes('Quota exceeded')) {
    // Set 60-second cooldown to protect free tier rate limits
    apiCooldownUntil = Date.now() + 60000;
    console.warn('[Gemini AI] Rate limit or quota reached (429). Entering 60s fallback mode to serve heuristic transit insights seamlessly.');
  } else {
    console.error('[Gemini AI] Error:', errMsg);
  }
}

export interface TransitInsightRequest {
  routeName: string;
  busNumber: string;
  currentSpeed: number;
  delayMinutes: number;
  trafficLevel: string;
  nextStopName: string;
  etaMinutes: number;
  passengerCount: number;
  capacity: number;
}

// In-memory cache for insights
const insightCache = new Map<string, { data: any; timestamp: number }>();
const assistantCache = new Map<string, { reply: string; timestamp: number }>();
const optimizeCache = new Map<string, { data: any; timestamp: number }>();

function buildHeuristicInsight(data: TransitInsightRequest) {
  const isDelayed = data.delayMinutes > 2;
  const isCrowded = data.passengerCount > data.capacity * 0.8;
  const isSpeedSlow = data.currentSpeed < 15 && data.currentSpeed > 0;

  let delayAnalysis = 'Operating within standard schedule window on steady traffic flow.';
  if (isDelayed) {
    delayAnalysis = `Bus is delayed by +${data.delayMinutes} min due to ${data.trafficLevel} congestion near key campus intersections.`;
  } else if (data.trafficLevel === 'heavy' || data.trafficLevel === 'gridlock') {
    delayAnalysis = `Approaching dense ${data.trafficLevel} traffic; headway time may increase by 2-3 minutes.`;
  } else if (isSpeedSlow) {
    delayAnalysis = `Speed reduced to ${data.currentSpeed} km/h around pedestrian crosswalks and campus speed humps.`;
  }

  let recommendation = 'Boarding is proceeding normally; track live stop ETA on map.';
  if (isCrowded) {
    recommendation = `High seat occupancy (${data.passengerCount}/${data.capacity}). Students at upcoming stops are advised to prepare early or consider the next shuttle.`;
  } else if (isDelayed) {
    recommendation = `Dispatcher recommendation: Priority green signal at Gate 1 or deploy express loop if delay exceeds 10m.`;
  } else if (data.etaMinutes <= 3) {
    recommendation = `Approaching ${data.nextStopName} in ~${data.etaMinutes} min. Please proceed to the designated boarding shelter.`;
  }

  return {
    summary: `Bus ${data.busNumber} is running on ${data.routeName}, heading toward ${data.nextStopName} with an estimated arrival in ${data.etaMinutes} min.`,
    delayAnalysis,
    recommendation,
    anomalyDetected: (isDelayed && data.trafficLevel === 'heavy') || isCrowded
  };
}

export async function generateTransitInsights(data: TransitInsightRequest): Promise<{
  summary: string;
  delayAnalysis: string;
  recommendation: string;
  anomalyDetected: boolean;
}> {
  // Cache key based on route, bus, next stop, delay and traffic
  const cacheKey = `${data.busNumber}-${data.routeName}-${data.nextStopName}-${data.delayMinutes}-${data.trafficLevel}-${Math.floor(data.etaMinutes / 2)}`;
  const cached = insightCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < 45000) {
    return cached.data;
  }

  const ai = getGenAI();

  if (!ai) {
    const heuristic = buildHeuristicInsight(data);
    insightCache.set(cacheKey, { data: heuristic, timestamp: Date.now() });
    return heuristic;
  }

  try {
    const prompt = `You are the Elite Bus AI Transit Intelligence Engine for an educational institution.
Analyze this active campus bus trip:
- Route: ${data.routeName}
- Bus: ${data.busNumber}
- Current Speed: ${data.currentSpeed} km/h
- Current Delay: ${data.delayMinutes} minutes
- Traffic Level: ${data.trafficLevel}
- Next Stop: ${data.nextStopName} (ETA: ${data.etaMinutes} minutes)
- Passenger Occupancy: ${data.passengerCount} / ${data.capacity} seats

Provide a concise JSON response with:
{
  "summary": "A 1-sentence real-time status summary for students and dispatchers",
  "delayAnalysis": "A 1-2 sentence explanation of why the bus is or is not delayed and how traffic affects it",
  "recommendation": "1 actionable suggestion for campus transport managers or waiting students",
  "anomalyDetected": boolean (true if unusual slowdown or unexpected crowding)
}
Return ONLY valid raw JSON with no Markdown wrappers.`;

    const response = await ai.models.generateContent({
      model: "gemini-3.7-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      },
    });

    const text = response.text?.trim() || "";
    const parsed = JSON.parse(text);
    const result = {
      summary: parsed.summary || `Bus ${data.busNumber} en route to ${data.nextStopName}`,
      delayAnalysis: parsed.delayAnalysis || 'Schedule running according to dynamic traffic parameters.',
      recommendation: parsed.recommendation || 'Track live ETA on the interactive map.',
      anomalyDetected: Boolean(parsed.anomalyDetected)
    };
    insightCache.set(cacheKey, { data: result, timestamp: Date.now() });
    return result;
  } catch (error) {
    handleGeminiError(error);
    const fallback = buildHeuristicInsight(data);
    insightCache.set(cacheKey, { data: fallback, timestamp: Date.now() });
    return fallback;
  }
}

function buildHeuristicAssistantReply(
  query: string,
  userRole: string,
  contextData: { activeBuses: number; routes: string[]; currentDelays: string }
): string {
  const q = query.toLowerCase();
  if (q.includes('privacy') || q.includes('track') || q.includes('gps') || q.includes('location')) {
    return 'Elite Bus Assistant: We strictly uphold a Zero-Tracking Privacy Policy. No student or faculty smartphone GPS is ever collected. Only active commercial buses transmit coordinates during scheduled driver trips.';
  }
  if (q.includes('delay') || q.includes('late') || q.includes('traffic')) {
    return `Elite Bus Assistant: ${contextData.currentDelays}. Active fleet consists of ${contextData.activeBuses} shuttles operating across ${contextData.routes.length} campus routes.`;
  }
  if (q.includes('driver') || q.includes('start trip')) {
    return 'Elite Bus Assistant: Drivers must select their assigned route and tap "Start Trip" on the Driver Dashboard to activate live telemetry and broadcast accurate ETAs to campus stops.';
  }
  if (q.includes('stop') || q.includes('time') || q.includes('schedule') || q.includes('when')) {
    return `Elite Bus Assistant: Real-time arrivals for all routes (${contextData.routes.join(', ')}) are updated via ML multi-factor predictions. Check the stop countdown list or interactive map for exact minute-by-minute ETAs.`;
  }
  return `Elite Bus Assistant: Currently monitoring ${contextData.activeBuses} active buses across ${contextData.routes.length} campus routes. ${contextData.currentDelays}. For live schedules, select your route on the main dashboard.`;
}

export async function askTransitAssistant(
  query: string,
  userRole: string,
  contextData: { activeBuses: number; routes: string[]; currentDelays: string }
): Promise<string> {
  const cacheKey = `${query.trim().toLowerCase()}-${userRole}-${contextData.activeBuses}`;
  const cached = assistantCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < 60000) {
    return cached.reply;
  }

  const ai = getGenAI();

  if (!ai) {
    const reply = buildHeuristicAssistantReply(query, userRole, contextData);
    assistantCache.set(cacheKey, { reply, timestamp: Date.now() });
    return reply;
  }

  try {
    const prompt = `You are the friendly, intelligent "Elite Bus AI Assistant" for the university campus transit system.
User Role: ${userRole}
Current Campus State:
- Active Buses: ${contextData.activeBuses}
- Available Routes: ${contextData.routes.join(', ')}
- Delay Status: ${contextData.currentDelays}

User Question: "${query}"

Guidelines:
- Give a polite, helpful, concise answer (under 80 words).
- Provide practical campus transit advice.
- Remember: Students and Staff are NEVER GPS tracked for privacy. Only buses provide GPS location during active driver trips.`;

    const response = await ai.models.generateContent({
      model: "gemini-3.7-flash",
      contents: prompt,
    });

    const reply = response.text?.trim() || buildHeuristicAssistantReply(query, userRole, contextData);
    assistantCache.set(cacheKey, { reply, timestamp: Date.now() });
    return reply;
  } catch (error) {
    handleGeminiError(error);
    const fallbackReply = buildHeuristicAssistantReply(query, userRole, contextData);
    assistantCache.set(cacheKey, { reply: fallbackReply, timestamp: Date.now() });
    return fallbackReply;
  }
}

export async function optimizeRouteSchedule(routeSummary: any): Promise<{
  analysis: string;
  recommendedHeadwayMinutes: number;
  congestionHotspots: string[];
  energyEfficiencyScore: number;
}> {
  const cacheKey = `optimize-${routeSummary?.routeNumber || 'default'}`;
  const cached = optimizeCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < 120000) {
    return cached.data;
  }

  const fallback = {
    analysis: `Route ${routeSummary?.routeNumber || 'R-01'} demonstrates steady corridor flow with minor dwell peaks during peak transition periods.`,
    recommendedHeadwayMinutes: 10,
    congestionHotspots: ['Campus Gate 1 Roundabout', 'Main Library Plaza'],
    energyEfficiencyScore: 89
  };

  const ai = getGenAI();

  if (!ai) {
    optimizeCache.set(cacheKey, { data: fallback, timestamp: Date.now() });
    return fallback;
  }

  try {
    const prompt = `You are a university transit route optimization AI.
Analyze this campus route data:
${JSON.stringify(routeSummary, null, 2)}

Provide JSON response:
{
  "analysis": "2 sentence strategic evaluation of route pacing and punctuality",
  "recommendedHeadwayMinutes": number (recommended interval between buses),
  "congestionHotspots": ["list of identified delay bottleneck areas"],
  "energyEfficiencyScore": number (0-100 score on fuel/battery optimization)
}
Return raw JSON only.`;

    const response = await ai.models.generateContent({
      model: "gemini-3.7-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      },
    });

    const parsed = JSON.parse(response.text?.trim() || "{}");
    const result = {
      analysis: parsed.analysis || fallback.analysis,
      recommendedHeadwayMinutes: Number(parsed.recommendedHeadwayMinutes) || 10,
      congestionHotspots: Array.isArray(parsed.congestionHotspots) ? parsed.congestionHotspots : fallback.congestionHotspots,
      energyEfficiencyScore: Number(parsed.energyEfficiencyScore) || 88
    };
    optimizeCache.set(cacheKey, { data: result, timestamp: Date.now() });
    return result;
  } catch (err) {
    handleGeminiError(err);
    optimizeCache.set(cacheKey, { data: fallback, timestamp: Date.now() });
    return fallback;
  }
}

