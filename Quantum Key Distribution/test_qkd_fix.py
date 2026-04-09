#!/usr/bin/env python3
"""
Test script to verify QKD simulation fix
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.services.qkd_service import qkd_service
    import asyncio

    # Test parameters
    test_parameters = {
        'key_length': 50,
        'noise_level': 5.0,
        'detector_efficiency': 95.0,
        'eavesdropper_present': False
    }

    print("🔍 Testing QKD simulation fix...")

    # Run the QKD protocol
    async def test_qkd():
        result = await qkd_service.run_bb84_protocol(test_parameters)

        if result['status'] == 'completed':
            print("✅ QKD simulation completed successfully!")
            print(f"✅ Session ID: {result['session_id']}")
            print(f"✅ Final key length: {len(result['final_key'])}")
            print(f"✅ Error rate: {result['error_rate']".2f"}%")
            print(f"✅ Security status: {result['security_status']}")
            return True
        else:
            print(f"❌ QKD simulation failed: {result.get('error', 'Unknown error')}")
            return False

    # Run the test
    success = asyncio.run(test_qkd())

    if success:
        print("\n🎉 QKD simulation fix verified!")
        print("The 'coroutine' object error has been resolved.")
    else:
        print("\n❌ QKD simulation still has issues.")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error during QKD test: {e}")
    sys.exit(1)
