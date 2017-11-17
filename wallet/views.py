import datetime

from django.shortcuts import render, redirect

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from .forms import SendingForm, ConnCredentialsForm


""" Helpers """
def _is_logged_in(request):
    return 'conn_credentials' in request.session

def _get_conn(rpcuser, rpcpassword, rpcconnect, rpcport):
    return AuthServiceProxy('http://{}:{}@{}:{}'.format(rpcuser, rpcpassword, rpcconnect, rpcport))


""" Views """
def index(request):
    if not _is_logged_in(request):
        return redirect('wallet:login')

    # Get connection
    conn = _get_conn(**request.session['conn_credentials'])

    # Handle sending
    if request.method == 'POST':
        sending_form = SendingForm(request.POST)
        if sending_form.is_valid():
            # Check RPC validity
            is_rpc_valid = True
            try:
                conn.sendtoaddress(sending_form.cleaned_data['address'],
                                   sending_form.cleaned_data['amount'])
            except Exception as e:
                is_rpc_valid = False
                sending_form.add_error(None, e)

            # If valid, then go back
            if is_rpc_valid:
                return redirect('wallet:index')
    else:
        sending_form = SendingForm()

    # Get balance
    balance = conn.getbalance()

    # Get address
    address = conn.getaccountaddress('')

    # Get transactions
    transactions = conn.listtransactions()[::-1]
    for t in transactions:
        t['datetime'] = datetime.datetime.fromtimestamp(t['time'])

    return render(request,
                  'wallet/index.html',
                  {'balance': balance,
                   'address': address,
                   'sending_form': sending_form,
                   'transactions': transactions})

def login(request):
    if _is_logged_in(request):
        return redirect('wallet:index')

    # Handle login
    if request.method == 'POST':
        conn_credentials_form = ConnCredentialsForm(request.POST)
        if conn_credentials_form.is_valid():
            # Try to establish a connection
            conn = _get_conn(**conn_credentials_form.cleaned_data)

            # Check RPC validity
            is_rpc_valid = True
            try:
                conn.getinfo()
            except Exception as e:
                is_rpc_valid = False
                conn_credentials_form.add_error(None, e)

            # If valid, then log the user in and go back
            if is_rpc_valid:
                request.session['conn_credentials'] = conn_credentials_form.cleaned_data
                return redirect('wallet:index')
    else:
        conn_credentials_form = ConnCredentialsForm()

    return render(request,
                  'wallet/login.html',
                  {'conn_credentials_form': conn_credentials_form})

def logout(request):
    if not _is_logged_in(request):
        return redirect('wallet:login')

    # Log the user out and go back
    request.session.pop('conn_credentials')
    return redirect('wallet:index')
