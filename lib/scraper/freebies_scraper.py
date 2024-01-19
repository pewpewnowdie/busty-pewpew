import requests
from bs4 import BeautifulSoup as bs

class FreebiesScraper:
    def get_soup(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = bs(response.text, 'html.parser')
        return soup

    def get_games(self, min_discount:int=None, min_rating:int=None, pages:int=None):
        game_list_data = []
        url = 'https://gg.deals/deals/'
        og_url = url
        if min_discount != None:
            url += '?minDiscount=' + str(min_discount)
        if url != og_url and min_rating != None:
            url += '&minRating=' + str(min_rating)
        else:
            url += '?minRating=' + str(min_rating)
        wpurl = url
        page = 0
        while True:
            page = page+1
            if pages and page > pages:
                break
            if url != og_url:
                url = wpurl + '&page='+str(page)
            else:
                url = wpurl + '?page='+str(page)
            soup = self.get_soup(url)
            if not soup:
                break
            game_list = soup.find_all('div', id='deals-list')[0]
            game_list = game_list.find_all('div', {'class':'game-list-item'})
            for game in game_list:
                game_data = {}
                game_info = game.find_all('div', {'class':'game-info-wrapper'})[0]
                game_data['title'] = game_info.find_all('div', {'class':'game-info-title-wrapper'})[0].text.strip()
                game_data['image'] = game.find_all('picture', {'class':'game-picture'})[0].find_all('img')[0]['src']
                try:
                    game_data['price-new'] = game_info.find_all('div', {'class':'price-wrapper'})[0].text.strip().split('\n')[1]
                    game_data['price-old'] = game_info.find_all('div', {'class':'price-wrapper'})[0].text.strip().split('\n')[0]
                except:
                    continue
                dura = game_info.find_all('span', {'class':'expiry'})
                game_data['duration'] = 'ends '+dura[0].text.strip().split('\xa0')[1] if dura else None
                game_data['shop-name'] = game.find_all('span', {'class':'shop-icon'})[0].find_all('img')[0]['alt']
                game_data['shop-link'] = 'https://gg.deals'+game.find_all('a', {'class':'shop-link'})[0]['href']
                game_list_data.append(game_data)
        return game_list_data

    def get_freebies(self, pages:int=None):
        return self.get_games(min_discount=100, min_rating=0, pages=pages)

scraper = FreebiesScraper()