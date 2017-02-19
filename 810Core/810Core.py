#********************************YIC********************************
#
#
#
#********************************YIC********************************
import                ssl
from functools import wraps
import                wrapper_scraper
import                datetime
import                threading
import                time
import                network

#------------------------------------------------------------------------------
#Don't know what this[sslwrap(func)] does honestly, but it should hopefully stop the crash resulting in the error:
#urlopen error [Errno 8] _ssl.c:504: EOF occurred in violation of protocol
#Source:http://stackoverflow.com/questions/11772847/error-urlopen-error-errno-8-ssl-c504-eof-occurred-in-violation-of-protoco
#This can be moved to the network module
#------------------------------------------------------------------------------
def sslwrap(func):
    @wraps(func)
    def bar(*args, **kw):
        kw['ssl_version'] = ssl.PROTOCOL_TLSv1
        return func(*args, **kw)
    return bar
    
ssl.wrap_socket = sslwrap(ssl.wrap_socket)


#open log file
log_date = '.'.join((str(datetime.datetime.now()).split(':'))[:-1])
log = open(log_date + '_LOG.txt', 'w')

#global time reference is necessary
epoch_ref = time.time()

#ticker data periodic callback
def ticker_periodic_callback(ticker, offset):
    global epoch_ref
    try:
        ticker.refresh()
        price = ticker.get_price()
        log.write(ticker.get_tick() + ' ' + str(price) + '   -   Sys Time: ' + str(datetime.datetime.now()) + '\n')
        print(ticker.get_tick() + ' ' + str(price) + '   -   Sys Time: ' + str(datetime.datetime.now()) + '\n')        
    except:
        log.write('Exception   -   Sys time: ' + str(datetime.datetime.now()) + '\n')

    epoch_ref = epoch_ref + offset #Add 1 second to the reference time for next run    
    ticker_thread = threading.Timer(epoch_ref - time.time(), ticker_periodic_callback, [ticker, offset])
    ticker_thread.start()


#use time.sleep() ONLY on initialization to help make times between callbacks more consistent
#offsets must be the same for all callbacks to have good spacing
print('System initialization begin...')
google_conn = network.check_connection('http://google.com/')
yic_conn = network.check_connection('http://yic.com/')

if (google_conn and yic_conn):
    #tickers to be pulled
    AAPL = wrapper_scraper.g_tick_data('AAPL')
    GOOG = wrapper_scraper.g_tick_data('GOOG')
    AMD = wrapper_scraper.g_tick_data('AMD')

    ticker_periodic_callback(AAPL, 1)
    time.sleep(1)
    ticker_periodic_callback(GOOG, 1)
    time.sleep(1)
    ticker_periodic_callback(AMD, 1)
    print('System initialization complete...')
    print('Running...')
else:
    print('System initialization failed...')