import praw
from random import randint
from os.path import join as joinpath

from ..web import download
from ..util.logger import log
from .imgur import Imgur
from ..util.config import config
from ..globals import Const
from .service import Service, ServiceException


subreddit_list =	['earthporn', 'wallpapers', 'wallpaperdump', 'specart', 'quotesporn', 'offensive_wallpapers',
		 	 'backgroundart', 'desktoplego', 'wallpaper', 'animewallpaper', 'nocontext_wallpapers',
			 'musicwallpapers', 'comicwalls',
			 'ImaginaryLandscapes+ImaginaryMonsters+ImaginaryCharacters+ImaginaryTechnology']
posts_limit = 10


class Reddit(Service):
	name = 'reddit'

	def __init__(self):
		self._subreddit_list = config.get_list('reddit', 'subreddit_list', default=subreddit_list)


	def get_image(self, pictures_dir, basename, query=None, color=None):
		subreddit = query
		if subreddit == None:
			subreddit = self._subreddit_list[randint(0, len(self._subreddit_list)-1)].strip()
		log.info('chosen subreddit: %s'%subreddit)

		reddit = praw.Reddit(user_agent=Const.app_name)
		posts = reddit.get_subreddit(subreddit).get_hot(limit=posts_limit)

		urls = [p.url for p in posts]
		retries = 3
		while retries > 0:
			try:
				url = urls[randint(0, len(urls) - 1)]
				ext = url[url.rfind('.')+1:]

				log.info('url: ' + url + ', extension: ' + ext)

				if ext not in Const.image_extensions:
					if url.find('imgur') != -1:
						imgur = Imgur()
						url = imgur.get_image_url_from_page(url)
						ext = url[url.rfind('.')+1:]
					else:
						log.debug('not a direct link to image')
						raise ServiceException()
				retries = 0
			except ServiceException:
				retries -= 1

		save_filepath = joinpath(pictures_dir, basename) + '.' + ext

		download(url, save_filepath)

		return basename + '.' + ext
