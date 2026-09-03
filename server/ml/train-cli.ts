import { runFullMLTrainingPipeline } from './train-and-evaluate';

try {
  const result = runFullMLTrainingPipeline();
  console.log('Training pipeline executed successfully!');
  console.log('Selected Model:', result.selectedModelName);
  process.exit(0);
} catch (error) {
  console.error('Training pipeline failed with error:', error);
  process.exit(1);
}
