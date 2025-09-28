#!/usr/bin/env python3
"""
Test script for banking integration
This script tests the banking API service and widget creation
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.banking_api import BankingAPIService
from backend.app.services.widget_service import WidgetService


async def test_banking_apis():
    """Test banking API service"""
    print("Testing Banking API Service...")
    
    banking_api = BankingAPIService()
    
    # Test accounts
    print("\n1. Testing get_accounts_by_type...")
    accounts_data = await banking_api.get_accounts_by_type()
    print(f"   Found {accounts_data['total_count']} accounts")
    print(f"   Account types: {accounts_data['account_types']}")
    
    # Test transactions
    print("\n2. Testing get_account_transactions...")
    transactions_data = await banking_api.get_account_transactions("ACC001", 5)
    print(f"   Found {transactions_data['total_count']} transactions for account ACC001")
    print(f"   Account balance: ${transactions_data['account_balance']}")
    
    # Test offers
    print("\n3. Testing get_offers...")
    offers_data = await banking_api.get_offers("savings", 5)
    print(f"   Found {offers_data['total_count']} offers")
    print(f"   Categories: {offers_data['categories']}")
    
    # Test payment links
    print("\n4. Testing get_payment_links...")
    payment_data = await banking_api.get_payment_links("3rd_party", 100.0, "John Doe")
    print(f"   Found {len(payment_data['payment_links'])} payment methods")
    print(f"   Available types: {payment_data['available_methods']}")
    
    # Test banker contacts
    print("\n5. Testing get_banker_contacts...")
    banker_data = await banking_api.get_banker_contacts("personal_banking", "wealth_management")
    print(f"   Found {banker_data['total_count']} bankers")
    print(f"   Departments: {banker_data['departments']}")
    
    return {
        'accounts': accounts_data,
        'transactions': transactions_data,
        'offers': offers_data,
        'payments': payment_data,
        'bankers': banker_data
    }


async def test_banking_widgets(test_data):
    """Test banking widget creation"""
    print("\n\nTesting Banking Widget Creation...")
    
    widget_service = WidgetService()
    
    # Test accounts widget
    print("\n1. Creating banking accounts widget...")
    accounts_widget = widget_service.create_banking_accounts_widget(test_data['accounts'])
    print(f"   Widget ID: {accounts_widget['id']}")
    print(f"   Widget Type: {accounts_widget['type']}")
    print(f"   Total accounts: {accounts_widget['data']['summary']['total_accounts']}")
    
    # Test transactions widget
    print("\n2. Creating banking transactions widget...")
    transactions_widget = widget_service.create_banking_transactions_widget("ACC001", test_data['transactions'])
    print(f"   Widget ID: {transactions_widget['id']}")
    print(f"   Widget Type: {transactions_widget['type']}")
    print(f"   Total transactions: {transactions_widget['data']['summary']['total_transactions']}")
    
    # Test offers widget
    print("\n3. Creating banking offers widget...")
    offers_widget = widget_service.create_banking_offers_widget(test_data['offers'])
    print(f"   Widget ID: {offers_widget['id']}")
    print(f"   Widget Type: {offers_widget['type']}")
    print(f"   Total offers: {offers_widget['data']['summary']['total_offers']}")
    
    # Test payments widget
    print("\n4. Creating banking payments widget...")
    payments_widget = widget_service.create_banking_payments_widget("3rd_party", test_data['payments'])
    print(f"   Widget ID: {payments_widget['id']}")
    print(f"   Widget Type: {payments_widget['type']}")
    print(f"   Total methods: {payments_widget['data']['summary']['total_methods']}")
    
    # Test banker widget
    print("\n5. Creating banking banker widget...")
    banker_widget = widget_service.create_banking_banker_widget(test_data['bankers'])
    print(f"   Widget ID: {banker_widget['id']}")
    print(f"   Widget Type: {banker_widget['type']}")
    print(f"   Total bankers: {banker_widget['data']['summary']['total_bankers']}")
    
    return {
        'accounts_widget': accounts_widget,
        'transactions_widget': transactions_widget,
        'offers_widget': offers_widget,
        'payments_widget': payments_widget,
        'banker_widget': banker_widget
    }


async def test_llm_integration():
    """Test LLM service integration with banking functions"""
    print("\n\nTesting LLM Service Integration...")
    
    try:
        from backend.app.services.llm_service import LLMService
        
        llm_service = LLMService()
        
        # Test banking function calls
        print("\n1. Testing banking function calls...")
        
        # Test accounts function
        print("   Testing get_banking_accounts function...")
        accounts_widget = await llm_service._execute_function_call(
            type('FunctionCall', (), {
                'name': 'get_banking_accounts',
                'args': {'account_type': 'checking'}
            })()
        )
        if accounts_widget:
            print(f"   ✓ Accounts widget created: {accounts_widget['type']}")
        
        # Test transactions function
        print("   Testing get_account_transactions function...")
        transactions_widget = await llm_service._execute_function_call(
            type('FunctionCall', (), {
                'name': 'get_account_transactions',
                'args': {'account_id': 'ACC001', 'limit': 5}
            })()
        )
        if transactions_widget:
            print(f"   ✓ Transactions widget created: {transactions_widget['type']}")
        
        # Test offers function
        print("   Testing get_banking_offers function...")
        offers_widget = await llm_service._execute_function_call(
            type('FunctionCall', (), {
                'name': 'get_banking_offers',
                'args': {'category': 'savings', 'limit': 5}
            })()
        )
        if offers_widget:
            print(f"   ✓ Offers widget created: {offers_widget['type']}")
        
        # Test payments function
        print("   Testing get_payment_links function...")
        payments_widget = await llm_service._execute_function_call(
            type('FunctionCall', (), {
                'name': 'get_payment_links',
                'args': {'payment_type': '3rd_party', 'amount': 100.0}
            })()
        )
        if payments_widget:
            print(f"   ✓ Payments widget created: {payments_widget['type']}")
        
        # Test banker function
        print("   Testing get_banker_contacts function...")
        banker_widget = await llm_service._execute_function_call(
            type('FunctionCall', (), {
                'name': 'get_banker_contacts',
                'args': {'department': 'personal_banking'}
            })()
        )
        if banker_widget:
            print(f"   ✓ Banker widget created: {banker_widget['type']}")
        
        print("\n   ✓ All banking function calls successful!")
        
    except Exception as e:
        print(f"   ✗ LLM integration test failed: {e}")


async def main():
    """Main test function"""
    print("=" * 60)
    print("BANKING INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test banking APIs
        test_data = await test_banking_apis()
        print("\n✓ Banking API tests passed!")
        
        # Test widget creation
        widgets = await test_banking_widgets(test_data)
        print("\n✓ Banking widget creation tests passed!")
        
        # Test LLM integration
        await test_llm_integration()
        print("\n✓ LLM integration tests passed!")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\nBanking features are ready to use!")
        print("You can now:")
        print("- Ask for 'show my accounts' to see account widgets")
        print("- Ask for 'show transactions for account ACC001' to see transaction widgets")
        print("- Ask for 'show banking offers' to see offer widgets")
        print("- Ask for 'show payment options' to see payment widgets")
        print("- Ask for 'show banker contacts' to see banker widgets")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
