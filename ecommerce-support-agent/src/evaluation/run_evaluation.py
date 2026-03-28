"""
Evaluation script for E-commerce Support Resolution Agent.
Runs test cases and calculates metrics as required by the assessment.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestration.crew import process_support_ticket


class SupportAgentEvaluator:
    """Evaluates the support agent system against test cases."""
    
    def __init__(self, test_cases_path: str, output_path: str):
        self.test_cases_path = test_cases_path
        self.output_path = output_path
        self.results = []
        
    def load_test_cases(self) -> List[Dict]:
        """Load test cases from JSON file."""
        with open(self.test_cases_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def has_citations(self, output: str) -> bool:
        """Check if output contains proper citations (POL-XXX format)."""
        citation_pattern = r'POL-\d{3}'
        return bool(re.search(citation_pattern, output))
    
    def count_citations(self, output: str) -> int:
        """Count number of citations in output."""
        citation_pattern = r'POL-\d{3}'
        return len(re.findall(citation_pattern, output))
    
    def check_unsupported_claims(self, output: str) -> Dict:
        """
        Check for unsupported claims (manual review rubric).
        Returns dict with flags for common issues.
        """
        issues = {
            'missing_citations': not self.has_citations(output),
            'vague_timeframes': bool(re.search(r'\b(soon|shortly|quickly)\b', output.lower())),
            'invented_prices': False,  # Would need more context to detect
            'no_policy_reference': 'policy' not in output.lower() and 'POL-' not in output,
        }
        return issues
    
    def determine_expected_decision(self, test_case: Dict) -> str:
        """Determine expected decision type based on test case category."""
        category = test_case.get('category', '')
        title = test_case.get('title', '').lower()
        
        if 'not in policy' in category.lower() or 'not covered' in title:
            return 'ESCALATED'
        elif 'ambiguous' in category.lower() or 'missing' in title:
            return 'NEEDS MORE INFO'
        elif 'conflict' in category.lower():
            return 'ESCALATED'
        else:
            return 'APPROVED_OR_DENIED'
    
    def evaluate_decision(self, output: str, expected: str) -> bool:
        """Check if decision matches expected type."""
        output_upper = output.upper()
        
        if expected == 'ESCALATED':
            return 'ESCALATED' in output_upper or 'ESCALATION' in output_upper
        elif expected == 'NEEDS MORE INFO':
            return 'NEEDS MORE INFO' in output_upper or 'CLARIFYING QUESTIONS' in output_upper
        elif expected == 'APPROVED_OR_DENIED':
            return 'APPROVED' in output_upper or 'DENIED' in output_upper
        
        return False
    
    def run_single_test(self, test_case: Dict) -> Dict:
        """Run a single test case and collect metrics."""
        print(f"\n{'='*60}")
        print(f"Running Test Case: {test_case['id']} - {test_case['title']}")
        print(f"{'='*60}")
        
        try:
            # Process the ticket
            result = process_support_ticket(test_case['ticket'])
            
            # Extract output
            final_output = str(result.get('final_output', ''))
            status = result.get('status', 'UNKNOWN')
            
            # Calculate metrics
            has_citations = self.has_citations(final_output)
            citation_count = self.count_citations(final_output)
            unsupported_issues = self.check_unsupported_claims(final_output)
            expected_decision = self.determine_expected_decision(test_case)
            correct_decision = self.evaluate_decision(final_output, expected_decision)
            
            # Compile results
            test_result = {
                'test_id': test_case['id'],
                'title': test_case['title'],
                'category': test_case['category'],
                'status': status,
                'has_citations': has_citations,
                'citation_count': citation_count,
                'unsupported_issues': unsupported_issues,
                'expected_decision': expected_decision,
                'correct_decision': correct_decision,
                'output_length': len(final_output),
                'success': status in ['SUCCESS', 'ESCALATED'] and has_citations,
            }
            
            print(f"✓ Test completed - Citations: {citation_count}, Decision: {status}")
            
            return test_result
            
        except Exception as e:
            print(f"✗ Test failed with error: {str(e)}")
            return {
                'test_id': test_case['id'],
                'title': test_case['title'],
                'category': test_case['category'],
                'status': 'ERROR',
                'error': str(e),
                'success': False,
            }
    
    def calculate_metrics(self, results: List[Dict]) -> Dict:
        """Calculate aggregate metrics from all test results."""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        
        # Citation coverage rate
        tests_with_citations = sum(1 for r in results if r.get('has_citations', False))
        citation_coverage = (tests_with_citations / total_tests * 100) if total_tests > 0 else 0
        
        # Unsupported claim rate
        total_issues = sum(
            sum(r.get('unsupported_issues', {}).values())
            for r in results
        )
        unsupported_rate = (total_issues / total_tests) if total_tests > 0 else 0
        
        # Correct escalation rate
        escalation_tests = [r for r in results if r.get('expected_decision') == 'ESCALATED']
        correct_escalations = sum(1 for r in escalation_tests if r.get('correct_decision', False))
        escalation_rate = (correct_escalations / len(escalation_tests) * 100) if escalation_tests else 0
        
        # Correct "needs info" rate
        needs_info_tests = [r for r in results if r.get('expected_decision') == 'NEEDS MORE INFO']
        correct_needs_info = sum(1 for r in needs_info_tests if r.get('correct_decision', False))
        needs_info_rate = (correct_needs_info / len(needs_info_tests) * 100) if needs_info_tests else 0
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            'citation_coverage_rate': citation_coverage,
            'unsupported_claim_rate': unsupported_rate,
            'correct_escalation_rate': escalation_rate,
            'correct_needs_info_rate': needs_info_rate,
            'total_citations': sum(r.get('citation_count', 0) for r in results),
            'avg_citations_per_test': sum(r.get('citation_count', 0) for r in results) / total_tests if total_tests > 0 else 0,
        }
    
    def run_evaluation(self):
        """Run full evaluation on all test cases."""
        print("\n" + "="*60)
        print("E-COMMERCE SUPPORT AGENT EVALUATION")
        print("="*60)
        
        # Load test cases
        test_cases = self.load_test_cases()
        print(f"\nLoaded {len(test_cases)} test cases")
        
        # Run each test
        for test_case in test_cases:
            result = self.run_single_test(test_case)
            self.results.append(result)
        
        # Calculate metrics
        metrics = self.calculate_metrics(self.results)
        
        # Print summary
        self.print_summary(metrics)
        
        # Save results
        self.save_results(metrics)
        
        return metrics
    
    def print_summary(self, metrics: Dict):
        """Print evaluation summary."""
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"\nTotal Tests: {metrics['total_tests']}")
        print(f"Successful Tests: {metrics['successful_tests']}")
        print(f"Success Rate: {metrics['success_rate']:.1f}%")
        print(f"\n--- REQUIRED METRICS ---")
        print(f"Citation Coverage Rate: {metrics['citation_coverage_rate']:.1f}%")
        print(f"Unsupported Claim Rate: {metrics['unsupported_claim_rate']:.2f} issues/test")
        print(f"Correct Escalation Rate: {metrics['correct_escalation_rate']:.1f}%")
        print(f"Correct 'Needs Info' Rate: {metrics['correct_needs_info_rate']:.1f}%")
        print(f"\n--- ADDITIONAL METRICS ---")
        print(f"Total Citations: {metrics['total_citations']}")
        print(f"Avg Citations per Test: {metrics['avg_citations_per_test']:.1f}")
        print("="*60)
    
    def save_results(self, metrics: Dict):
        """Save results to JSON file."""
        output = {
            'evaluation_date': datetime.now().isoformat(),
            'metrics': metrics,
            'detailed_results': self.results,
        }
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Results saved to: {self.output_path}")


def main():
    """Main evaluation function."""
    base_dir = Path(__file__).parent.parent.parent
    
    # Test both standard and tricky test cases
    test_files = [
        base_dir / "data" / "test_cases" / "test_tickets.json",
        base_dir / "data" / "test_cases" / "tricky_test_tickets.json",
    ]
    
    all_results = []
    
    for test_file in test_files:
        if test_file.exists():
            print(f"\n{'='*60}")
            print(f"Evaluating: {test_file.name}")
            print(f"{'='*60}")
            
            output_file = base_dir / "evaluation" / f"results_{test_file.stem}.json"
            
            evaluator = SupportAgentEvaluator(
                test_cases_path=str(test_file),
                output_path=str(output_file)
            )
            
            metrics = evaluator.run_evaluation()
            all_results.append({
                'file': test_file.name,
                'metrics': metrics
            })
    
    # Save combined summary
    combined_output = base_dir / "evaluation" / "results_summary.json"
    with open(combined_output, 'w', encoding='utf-8') as f:
        json.dump({
            'evaluation_date': datetime.now().isoformat(),
            'test_files': all_results
        }, f, indent=2)
    
    print(f"\n✓ Combined summary saved to: {combined_output}")


if __name__ == "__main__":
    main()
