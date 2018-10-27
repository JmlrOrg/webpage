import http.server
import socketserver
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

PORT = 8010

web_dir = os.path.join(os.path.dirname(__file__), '../output/')
os.chdir(web_dir)

class StoppableHTTPServer(http.server.HTTPServer):
    def run(self):
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # Clean-up server (close socket, etc.)
            self.server_close()



def test_1(driver):
    print('Test 1')

    driver.get("http://localhost:%s" % PORT)
    assert "Journal of Machine Learning Research" in driver.title
    # elem = driver.find_element_by_name("q")
    # elem.clear()
    # elem.send_keys("pycon")
    # elem.send_keys(Keys.RETURN)
    # assert "No results found." not in driver.page_source


def test_2(driver):
    pass


all_tests = [test_1, test_2]

if __name__ == '__main__':
    print('Starting server')
    server = StoppableHTTPServer(("localhost", PORT),
                                 http.server.SimpleHTTPRequestHandler)
    # Start processing requests
    thread = threading.Thread(None, server.run)
    thread.start()
    print('Server started')

    print('Launching headless Chrome')
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--log-path=chromedriver.log')
    options.add_argument('--verbose')
    driver = webdriver.Chrome(options=options)
    prin('headless Chrome launched')

    for t in all_tests:
        t(driver)

    driver.close()

    # Shutdown server
    server.shutdown()
    thread.join()
