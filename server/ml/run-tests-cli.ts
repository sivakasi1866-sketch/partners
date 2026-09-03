import { runComprehensiveTestSuite } from './tests/ml-pipeline.test';

const results = runComprehensiveTestSuite();
if (results.failedTests > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
