import logging
logging.basicConfig(
    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO, filemode='w', filename='test.log')
try:
    logging.info('1231'.decode())
except:
    logging.info('1231123')
print(12312412)
