#!/usr/bin/env python3
"""
Test script to verify the refactored RoutingAgent works without global instance issues.
"""

import asyncio
import os
from routing_agent import RoutingAgent

async def test_routing_agent_creation():
    """Test that RoutingAgent can be created without global instance issues."""
    print("Testing RoutingAgent creation...")
    
    try:
        # Test 1: Create a RoutingAgent instance
        routing_agent = await RoutingAgent.create(
            remote_agent_addresses=[
                'http://localhost:10001',  # Mock URL for testing
                'http://localhost:10002',  # Mock URL for testing
            ]
        )
        
        print("✅ RoutingAgent created successfully")
        print(f"   - Initialized: {routing_agent.is_initialized}")
        print(f"   - Remote agents: {len(routing_agent.remote_agent_connections)}")
        
        # Test 2: Check that we can create the Azure agent (will fail without proper env vars)
        try:
            azure_agent = routing_agent.create_agent()
            print("✅ Azure AI agent created successfully")
            print(f"   - Agent ID: {azure_agent.id}")
        except Exception as e:
            print(f"⚠️  Azure AI agent creation failed (expected without env vars): {e}")
        
        # Test 3: Cleanup
        #routing_agent.cleanup()
        #print("✅ RoutingAgent cleaned up successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_routing_agent_creation())
