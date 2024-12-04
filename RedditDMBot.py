from modules import *



# Initializing components
config, links, paths, locators = getConfig(), getLinks(), getPaths(), getLocators()
list_usernames, usernames_sent = list(), list()
#

class Modules:
    """
        Modules class, this class holds all the non-main functions the program needs for better functionality.
    """

    Format = {
        'GREEN':'\033[92m',
        'YELLOW':'\033[93m',
        'RED':'\033[91m',
        'END':'\033[0m'
    }

    @staticmethod
    def log(index: int, data: str) -> None:
        """
            Logging system. Not necessary, but good and useful.
        """
        
        # managing different inputs to output them in different colors
        if(index == -1): # neutral input, no color
            print(f'[{str(datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"))}] - {data}')
        elif(index == 0): # success input, green
            print(f'{Modules.Format["GREEN"]}[{str(datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"))}] - {data}{Modules.Format["END"]}')
        elif(index == 1): # error input, yellow
            print(f'{Modules.Format["YELLOW"]}[{str(datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"))}] - {data}{Modules.Format["END"]}')
        elif(index == 2): # fatal error input, red
            print(f'{Modules.Format["RED"]}[{str(datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"))}] - {data}{Modules.Format["END"]}')

        with open('logs/log', 'a') as log:
            log.write(f'[{str(datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"))}] - {data}\n')

    @staticmethod
    def dbToList(database: str, list_usernames: list) -> None: # to get all usernames from usernames.csv into list_usernames
        """
            retrieving data from a CSV database
        """
        with open(database, 'r') as usernames:
            dbReader = reader(usernames, delimiter=',')
            for row in dbReader:
                list_usernames.append(
                    str(row[0])
                )

    @staticmethod
    def writeToCSV(database: str, data: list) -> None:
        """
            saving data to a CSV database
        """
        with open(database, 'a', newline='', encoding='utf-8') as db:
            _writer = writer(db)
            _writer.writerow(
                data
            )
    
    @staticmethod
    def manageProxyExtension(index: int, proxy_backend_path: str, proxy: str) -> None:
        """
            this function is responsible for adding and removing proxy from rsrc/extensions/proxy
            this is a really important function that would enable the software to rotate between proxies
        """
        try:

            if(index == 0): # removing proxy

                proxyList, proxy_backend = proxy.split(':'), str()
                host, port, username, password = proxyList[0], proxyList[1], proxyList[2], proxyList[3]
                with open(proxy_backend_path, 'r') as proxy_backend_js:
                    proxy_backend = proxy_backend_js.read()
                proxy_backend = proxy_backend.replace(host, '_host').replace(port, '_port').replace(username, '_username').replace(password, '_password')
                with open(proxy_backend_path, 'w') as proxy_backend_js:
                    proxy_backend_js.write(proxy_backend)
                Modules.log(0, f'[RedditDMBot] - Proxy {proxy} was removed successfully.')

            elif(index == 1): # adding proxy

                proxyList, proxy_backend = proxy.split(':'), str()
                host, port, username, password = proxyList[0], proxyList[1], proxyList[2], proxyList[3]
                with open(proxy_backend_path, 'r') as proxy_backend_js:
                    proxy_backend = proxy_backend_js.read()
                proxy_backend = proxy_backend.replace('_host', host).replace('_port', port).replace('_username', username).replace('_password', password)
                with open(proxy_backend_path, 'w') as proxy_backend_js:
                    proxy_backend_js.write(proxy_backend)
                Modules.log(0, f'[RedditDMBot] - Proxy {proxy} was removed successfully.')

        except:

            #import traceback
            # logging out the error
            #Modules.log(2, traceback.format_exc())
            Modules.log(2, '[RedditDMBot] - Fatal error while trying to setup Proxy extension.')


    # getting necessary data: configuration, Reddit account(s), locators of Reddit pages, necessary links, and more for the program to function

    @staticmethod
    def getProxies() -> list:
        with open('rsrc/proxies.json','r') as proxies:
            return load(proxies)

    @staticmethod
    def getPaths() -> dict: # managing relative paths in case this program needs to run on multiple computers with different paths to resources
        with open('rsrc/paths.json','r') as config:
            return load(config)

    @staticmethod
    def getConfig() -> dict:
        with open('rsrc/config.json','r') as config:
            return load(config)

    @staticmethod
    def getLocators() -> dict:
        with open('rsrc/locators.json','r') as locators:
            return load(locators)

    @staticmethod
    def getLinks() -> dict:
        with open('rsrc/links.json','r') as links:
            return load(links)

    # getting JavaScript code to execute inside CD
    @staticmethod
    def getJS(path) -> str:
        with open(path, 'r') as JS:
            return str(JS.read())

    # getting a list of the most common user agents to use
    @staticmethod
    def getUserAgents() -> list:
        with open('rsrc/user_agents.json','r') as user_agents:
            return load(user_agents)




async def RedditDMBot(
        config: dict,
        links: dict,
        paths: dict,
        proxy: str,
        used_accounts: list,
        account: dict,
        target: str
) -> None:
    """
        main function responsible for sending a DM
    """
    # initializing a config instance for the browser
    browser_config = nodriver.Config()

    # headless or headfull?
    browser_config.headless = config['headless']

    # adding arguments to the configuration to initiate the browser with
    browser_config.browser_args = config['browser_args']

    # changing proxy configuration to add to the browser
    if(proxy != 'localhost'): # in case there are proxies for the software to use

        Modules.manageProxyExtension(
            index = 1,
            proxy_backend_path = paths['proxy']['proxy_backend_path'],
            proxy = proxy
        )
        ip = loads(
                get(
                    links['GET_CONNECTION_IP'],
                    proxies={
                        'http':f"http://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}",
                        "https":f"http://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"
                    }
                ).text
            )['origin']
        
        browser_config.add_extension( # adding proxy extension
            extension_path = paths['proxy']['proxy_extension_path']
        )
        
    else: # in case no proxy was provided

        ip = loads(
                get(
                    links['GET_CONNECTION_IP']
                ).text
            )['origin']

    # initializing a browser of nodriver
    browser = await nodriver.start(
        config = browser_config
    )

    # creating an instance by navigating to Reddit's login page

    instance = browser.get(links['REDDIT_LOGIN_PAGE_URL'])

    async with async_playwright() as playwright:
        device = playwright.devices['Desktop Chrome']
        if(config['proxy']['proxy'] == 'localhost'):
            browser = await playwright.chromium.launch(
                headless = config['headless']
            )
            ip = loads(
                get(
                    links['getConnectionIP']
                ).text
            )['origin']
        else:
            browser = await playwright.chromium.launch(
                headless = config['headless'],
                proxy = {
                    "server":f"{config['proxy']['proxy'].split(':')[0]}:{config['proxy']['proxy'].split(':')[1]}",
                    "username":config['proxy']['proxy'].split(':')[2],
                    "password":config['proxy']['proxy'].split(':')[3]
                }
            )
            ip = loads(
                get(
                    links['getConnectionIP'],
                    proxies={
                        'http':f"http://{config['proxy']['proxy'].split(':')[2]}:{config['proxy']['proxy'].split(':')[3]}@{config['proxy']['proxy'].split(':')[0]}:{config['proxy']['proxy'].split(':')[1]}",
                        "https":f"http://{config['proxy']['proxy'].split(':')[2]}:{config['proxy']['proxy'].split(':')[3]}@{config['proxy']['proxy'].split(':')[0]}:{config['proxy']['proxy'].split(':')[1]}"
                    }
                ).text
            )['origin']
        context = await browser.new_context(**device)
        #context.set_default_timeout(5000)
        page = await context.new_page()
        await stealth_async(page)
        try:
            await page.goto(links['REDDIT_LOGIN_PAGE_URL'])
            await page.wait_for_load_state('networkidle')
            await page.locator(locators['usernameLocator']).fill(account['username'])
            await page.locator(locators['passwordLocator']).fill(account['password'])
            await page.locator(locators['loginButtonLocator']).click()
            sleep(uniform(2,3))
            log(f'[Main] Successfuly logged in to Reddit account {account["username"]}:{account["password"]} through {ip}')
            await page.goto(f'{links["MESSAGE_URL"]}/{username}')
            sleep(config['cooldown'])
            await page.locator(locators['messageInputLocator']).fill(choice(config['messages']))
            #async with page.expect_response(f'{links["MESSAGE_URL"]}/{username}') as response:
            await page.locator(locators['sendButtonLocator']).click()
            sleep(uniform(1,2))
            try:
                await page.locator(locators['unableToDMCloseLocator']).click( timeout = 2000 )
                log(f'[Main] {account["username"]} was unable to send DM. Writing it to the database...')
                writeToCSV(
                    paths['toss_accounts'],
                    [
                        account['username'],
                        account['password']
                    ]
                )
                await page.screenshot( path=f"results/failed/{account['username']}_to_{username}#{await page.locator(locators['chatReceiverLocator']).get_attribute('title')}.png" )
            except:
                log(f'[Main] Message sent to {username}#{await page.locator(locators["roomReceiverLocator"]).get_attribute("title")} using {account["username"]}. Writing it to the database...')
                writeToCSV(
                    paths['usernames_sent'],
                    [
                        username,
                        account['username']
                    ]
                )
                await page.screenshot( path=f"results/succeeded/{account['username']}_to_{username}#{await page.locator(locators['roomReceiverLocator']).get_attribute('title')}.png" )
                list_usernames.remove(username) # removing that username from the list of usernames to DM
                used_accounts.append(account) # adding account to the list of used accounts
        except:
            log(f'[Main] ERROR! An exception occured while trying to DM {username} using {account["username"]}:{account["password"]}.')
            writeToCSV(
                paths['usernames_failed'],
                [
                    username,
                    account['username']
                ]
            )
        finally:
            if(config['proxy']['proxyRotationLink'] != ''):
                log('[Main] Rotating proxy IP...')
                get(config['proxy']['proxyRotationLink'])
                sleep(config['proxy']['proxyRotationCooldown'])
            await browser.close()


def main():
    dbToList(paths['usernames'],list_usernames)
    accounts, used_accounts = getAccounts(), list()
    while(len(list_usernames) != 0): # while there are usernames to send DM to
        username = choice(list_usernames) # getting a random username from the list of usernames to DM
        if(len(accounts) == 0): # to check if all accounts are used
            accounts, used_accounts = used_accounts, list() # repopulates accounts with used_accounts and reinitialize used_accounts to an empty list
        try:
            account = accounts.pop(0) # getting the first account of the list accounts, then removing it
        except IndexError:
            log('[Main] There are no more useful accounts to use.')
            break
        asyncio.run(RedditDMBot(used_accounts,account,username)) # entry point
    log('[Main] Done.')




if __name__ == '__main__':
    main()