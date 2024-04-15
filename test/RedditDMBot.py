from modules import *



# Initializing components
config, links, paths, locators = getConfig(), getLinks(), getPaths(), getLocators()
list_usernames, usernames_sent = list(), list()
#




async def RedditDMBot(used_accounts,account,username):
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