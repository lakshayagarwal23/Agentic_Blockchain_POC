#!/usr/bin/env python3
import time
import requests
import json
import sys
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint and measure response time"""
    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            raise ValueError("Unsupported HTTP method")

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # in milliseconds

        return {
            'endpoint': endpoint,
            'method': method,
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2),
            'success': response.status_code < 400
        }

    except Exception as e:
        return {
            'endpoint': endpoint,
            'method': method,
            'error': str(e),
            'success': False
        }

def run_performance_tests():
    print("🚀 Running Performance Tests")
    print("=" * 50)

    test_cases = [
        ('/api/health', 'GET'),
        ('/api/stats', 'GET'),
        ('/', 'GET'),
        ('/static/css/style.css', 'GET'),
        ('/static/js/app.js', 'GET'),
        ('/api/intake', 'POST', {
            'wallet_address': '0x742d35Cc6e34d8d7C15fE14c123456789abcdef0',
            'user_input': 'Tokenize my $100,000 car, a 2020 Honda Civic',
            'email': 'test@example.com'
        })
    ]

    results = []

    for case in test_cases:
        endpoint = case[0]
        method = case[1]
        data = case[2] if len(case) > 2 else None

        print(f"Testing {method} {endpoint}...")
        result = test_endpoint(endpoint, method, data)
        results.append(result)

        if result['success']:
            print(f"✅ {result['response_time_ms']} ms")
        else:
            error_msg = result.get("error") or f"HTTP {result.get('status_code', 'N/A')}"
            print(f"❌ Failed: {error_msg}")

    print("\n📊 Performance Summary:")
    print("=" * 50)

    successful = [r for r in results if r['success']]
    if successful:
        avg = sum(r['response_time_ms'] for r in successful) / len(successful)
        print(f"✅ Successful requests: {len(successful)}/{len(results)}")
        print(f"📈 Average Response Time: {avg:.2f} ms")
    else:
        print("❌ No successful responses")

def load_test(num_requests=10):
    """Simple load test on /api/health"""
    print(f"\n🔥 Load Testing with {num_requests} concurrent requests")
    print("=" * 50)

    def make_request():
        return test_endpoint('/api/health')

    start = time.time()
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [f.result() for f in futures]
    end = time.time()

    total_time = end - start
    successful = [r for r in results if r['success']]
    if successful:
        avg = sum(r['response_time_ms'] for r in successful) / len(successful)
        print(f"✅ Successful: {len(successful)}/{num_requests}")
        print(f"⏱ Total Time: {total_time:.2f} seconds")
        print(f"📊 Requests/sec: {num_requests / total_time:.2f}")
        print(f"📈 Avg Response Time: {avg:.2f} ms")
    else:
        print("❌ All load test requests failed")

if __name__ == '__main__':
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=3)
    except:
        print("❌ Server is not running. Please start the application first.")
        sys.exit(1)

    run_performance_tests()
    load_test(10)
