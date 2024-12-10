from modules import *



# Initializing components
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
    def getAccounts() -> list:
        with open('rdt/accounts.json','r') as accounts:
            return load(accounts)

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
        locators: dict,
        proxy: str,
        used_accounts: list,
        account: dict,
        target: str
) -> None:
    """
        main function responsible for sending a DM
    """
    try:
        # initializing a config instance for the browser
        browser_config = nodriver.Config(
            browser_args = config['browser_args']
        )

        # headless or headfull?
        browser_config.headless = config['headless']

        # adding arguments to the configuration to initiate the browser with
        #browser_config.browser_args = config['browser_args']

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

            try:
                ip = loads(
                    get(
                        links['GET_CONNECTION_IP']
                    ).text
                )['origin']
            except:
                pass

        # initializing a browser of nodriver
        browser = await nodriver.start(
            config = browser_config
        )

        # creating an instance by navigating to Reddit's login page
        instance = await browser.get(links['REDDIT_LOGIN_PAGE_URL'])

        try: # logging in to Reddit

            # finding the username input and filling it
            username_input = await instance.select(locators['username_input_locator'], timeout = 5)
            await username_input.send_keys(account['username'])

            # finding the password input and filling it
            password_input = await instance.select(locators['password_input_locator'], timeout = 5)
            await password_input.send_keys(account['password'])

            # finding and clicking the log in button
            login_button = await instance.find('Log In', best_match = True)
            await login_button.click()

        except TimeoutError: # incase of wrong locators

            # closing browser
            await instance.close()
            #await browser.stop()

            # rerunning RedditDMBot with the same account and username to DM
            return asyncio.run(
                RedditDMBot(
                    config = config,
                    links = links,
                    paths = paths,
                    locators = locators,
                    proxy = proxy,
                    used_accounts = used_accounts,
                    account = account,
                    target = username
                )
            )
        
        except: # in case of other error

            Modules.log(2, f'[RedditDMBot] - An error occured while trying to login to Reddit account {account["username"]}:{account["password"]} @ {ip}.')

        Modules.log(0, f'[RedditDMBot] - Successfully logged in to Reddit account {account["username"]}:{account["password"]} @ {ip}.')

        sleep(config['cooldown'])

        # sending DM

        # getting the id of our target first
        await instance.get(f'{links["REDDIT_USER_PAGE_URL"]}/{target}')
        reddit_user_data_element = await instance.find(locators['reddit_user_data_locator'])
        target_id = loads(reddit_user_data_element.attributes[1])['profile']['id']

        sleep(config['cooldown'])

        # getting the chat page
        await instance.get(f'{links["REDDIT_MESSAGE_PAGE_URL"]}/{target_id}')

        sleep(config['cooldown'])
        
        # writing the message
        message_input = await instance.find('Message', best_match = True)
        await message_input.send_keys('HELLOOOOOOO')

        send_message_button = await instance.find('Send message', best_match = True)
        await send_message_button.click()

        Modules.log(0, f'[RedditDMBot] - Message sent successfully to {target} using Reddit account {account["username"]}:{account["password"]} @ {ip}')
        
        sleep(config['cooldown'])

    except:
        
        await Modules.log(2, f'[RedditDMBot] - An error occured while trying to DM {target} with Reddit account {account["username"]}:{account["password"]} @ {ip}.')

    finally: # finally rotating proxy IP if a rotation link exists

        if(config['proxy']['proxy_type'] == 'rotative'):
            if(config['proxy']['proxy_rotation_link'] != ''):
                Modules.log(-1, '[RedditDMBot] Rotating proxy IP...')
                get(config['proxy']['proxy_rotation_link'])
                sleep(config['proxy']['proxy_rotation_link'])
            else:
                Modules.log(2, '[RedditDMBot] - A proxy rotation link must be provided to rotate the proxy!')
                exit()

        # closing the instance and the browser
        await instance.close()
        #await browser.stop()

        sleep(config['cooldown'])








if __name__ == '__main__': # software entry point

    config, paths, links, locators = Modules.getConfig(), Modules.getPaths(), Modules.getLinks(), Modules.getLocators()
    proxies_pool = Modules.getProxies()

    Modules.dbToList(paths['usernames'], list_usernames)

    accounts, used_accounts = Modules.getAccounts(), list()

    while(len(list_usernames) != 0): # while there are usernames to send DM to

        username = choice(list_usernames) # getting a random username from the list of usernames to DM

        # choosing an account to send the DM with
        if(len(accounts) == 0): # to check if all accounts are used
            accounts, used_accounts = used_accounts, list() # repopulates accounts with used_accounts and reinitialize used_accounts to an empty list
        try:
            account = accounts.pop(0) # getting the first account of the list accounts, then removing it
        except IndexError: # in case no more accounts are in the accounts list
            Modules.log(1, '[RedditDMBot] There are no more useful accounts to use.')
            break

        # choosing a proxy to use
        if(config['proxy']['proxy_type'] == 'localhost'): proxy = 'localhost'
        elif(config['proxy']['proxy_type'] == 'sticky'):
            try:
                proxy = proxies_pool['sticky'].pop(0)
            except IndexError:
                Modules.log(1, '[RedditDMBot] There are no more useful proxies to use.')
                break
        elif(config['proxy']['proxy_type'] == 'rotative'):
            proxy = proxies_pool['rotative'][0]

        asyncio.run(
            RedditDMBot(
                config = config,
                links = links,
                paths = paths,
                locators = locators,
                proxy = proxy,
                used_accounts = used_accounts,
                account = account,
                target = username
            )
        ) # entry point

        # appending the account we used to 
        used_accounts.append(account)

        # removing the user we DMed from the list of usernames
        list_usernames.remove(username)
        usernames_sent.append(username)

        # adding the user we DMed alongside the account we used to DM to db/usernames_sent.csv
        Modules.writeToCSV(
            paths['usernames_sent'],
            [
                username,
                account['username']
            ]
        )

    Modules.log(-1, '[RedditDMBot] - Done.')