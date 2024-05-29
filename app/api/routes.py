from aiohttp import web
from app.models import User, Transaction
import uuid
from sqlalchemy import and_, select, func
import json
from datetime import datetime

async def create_user(request):
    data = await request.json()
    async with request.app['db'].acquire() as conn:
        async with conn.transaction():
            user = await User.create(name=data['name'], balance=0.00)
    return web.json_response({
        'id': user.id,
        'name': user.name,
    }, status=201)

async def add_transaction(request):
    data = await request.json()
    async with request.app['db'].acquire() as conn:
        async with conn.transaction():
            user = await User.get(int(data['user_id']))
            if not user:
                return web.json_response({'error': 'User not found'}, status=404)

            existing_txn = await Transaction.query.where(Transaction.uid == data['uid']).gino.first()
            if existing_txn:
                return web.json_response({
                    'id': existing_txn.id,
                    'type': existing_txn.type,
                    'amount': existing_txn.amount,
                }, status=200)

            amount = float(data['amount'])
            new_balance = user.balance + amount if data['type'] == 'DEPOSIT' else user.balance - amount

            if new_balance < 0:
                return web.json_response({'error': 'Insufficient funds'}, status=402)

            txn_timestamp = datetime.fromisoformat(data['timestamp'])

            txn = await Transaction.create(
                id=str(uuid.uuid4()),
                uid=data['uid'],
                type=data['type'],
                amount=amount,
                user_id=user.id,
                timestamp=txn_timestamp
            )

            await user.update(balance=new_balance).apply()

    return web.json_response({
        'id': txn.id,
        'type': txn.type,
        'amount': txn.amount,
    }, status=200)

async def get_transaction(request):
    txn_uid = request.match_info['id']
    async with request.app['db'].acquire() as conn:
        txn = await Transaction.query.where(Transaction.uid == txn_uid).gino.first()
        if not txn:
            return web.json_response({'error': 'Transaction not found'}, status=404)
    return web.json_response({
        'id': txn.id,
        'uid': txn.uid,
        'type': txn.type,
        'amount': txn.amount,
        'timestamp': txn.timestamp.isoformat(),
    }, status=200)

async def get_user_balance(request):
    user_id = request.match_info['id']
    date = request.query.get('date')
    async with request.app['db'].acquire() as conn:
        user = await User.get(int(user_id))
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)

        if date:
            date_obj = datetime.fromisoformat(date)
            deposits_query = select([func.sum(Transaction.amount)]).where(
                and_(Transaction.user_id == user.id, Transaction.timestamp <= date_obj, Transaction.type == 'DEPOSIT')
            )
            deposits_result = await conn.scalar(deposits_query)
            deposits = deposits_result if deposits_result is not None else 0.0

            withdrawals_query = select([func.sum(Transaction.amount)]).where(
                and_(Transaction.user_id == user.id, Transaction.timestamp <= date_obj, Transaction.type == 'WITHDRAW')
            )
            withdrawals_result = await conn.scalar(withdrawals_query)
            withdrawals = withdrawals_result if withdrawals_result is not None else 0.0

            balance = deposits - withdrawals
        else:
            balance = user.balance

    return web.json_response({
        'id': user.id,
        'balance': balance,
    }, status=200)

def add_routes(app):
    app.router.add_route('POST', '/v1/user', create_user, name='create_user')
    app.router.add_route('GET', '/v1/user/{id}/balance', get_user_balance, name='get_user_balance')
    app.router.add_route('PUT', '/v1/transaction', add_transaction, name='add_transaction')
    app.router.add_route('GET', '/v1/transaction/{id}', get_transaction, name='get_transaction')
