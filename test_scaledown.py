import requests
import json

# Test Java to Python conversion with ScaleDown
java_code = """
public class Test {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
"""

try:
    resp = requests.post(
        'http://127.0.0.1:8000/modernize',
        json={
            'code': java_code,
            'source_language': 'java',
            'target_language': 'python'
        },
        timeout=30
    )
    
    print(f"Status: {resp.status_code}")
    result = resp.json()
    print(f"Success: {result.get('success')}")
    
    if result.get('success'):
        print(f"\n✅ Modernization successful!")
        print(f"\nModernized Code:\n{result.get('modernized_code')}")
        print(f"\nMetrics: {result.get('metrics')}")
    else:
        print(f"❌ Error: {result.get('error')}")
        
except Exception as e:
    print(f"❌ Request failed: {e}")
