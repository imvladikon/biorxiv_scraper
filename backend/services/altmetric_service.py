import json
import requests
from injector import inject

AlTMETRIC_KEY="3c130976ca2b8f2e88f8377633751ba1"

class AltmetricException(Exception):
    pass

# https://biorxiv.altmetric.com/details/80489219
# https://api.altmetric.com/v1/doi/10.1101/2020.04.23.055293?callback=_altmetric.embed_callback&domain=www.biorxiv.org&key=3c130976ca2b8f2e88f8377633751ba1&cache_until=3-25
class AltmetricService(object):
    @inject
    def __init__(self):
        pass

    def get(self, doi):
        if not doi:
            return None
        a = Altmetric()
        return Citation(a.doi(doi))

class HTTPException(Exception):
    def __init__(self, status_code, message):
        super(HTTPException, self).__init__(status_code, message)
        self.status_code = status_code
        self.message = message

class Altmetric(object):
    """
    Altmetric builds a URL to query the Altmetric.com database. The response 
    from Altmetric is a dict.
    
    Usage:

        a = Altmetric()
        a.citations("1w", num_results=100, cited_in='reddit')
        a.doi('10.1038/nature1379')

    More information on querying the database and response object is available
    at api.altmetric.com.
    """
    host = "http://api.altmetric.com/"
    api_version = "v1/"
    base_url = host + api_version

    def __init__(self, api_key=AlTMETRIC_KEY):
        self.params = {}
        if api_key:
            self.params = {'key': api_key}

    def __getattr__(self, mode):
        def get(self, *args, **kwargs):
            return self.fetch(mode, *args, **kwargs)

        return get.__get__(self)

    def __repr__(self):
        if self.api_key:
            return '<Altmetric %s: %s>' % (self.api_version, self.api_key)
        else:
            return '<Altmetric %s>' % self.api_version

    def fetch(self, mode, *args, **kwargs):
        url = self.base_url + mode + "/" + "/".join([a for a in args])
        if kwargs != None:
            self.params.update(kwargs)

        try:
            response = requests.get(url, params=self.params)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 404 and response.reason == 'Not Found':
                return None
            raise HTTPException(response.status_code, response.reason)
        else:
            try:
                return response.json()
            except ValueError as e:
                raise AltmetricException(e.message)


class Citation(object):
    """
    Citation is initialized using a response object from the Altmetric class. 
    These are succesful responses from all modes ('doi', 'id', etc.), 
    except 'citations'.

    Usage:
        
        a = Altmetric()
        c = a.id("108989")  
        
        c = Citation(b) # or Citation(a.id("108989"))
        print c.title
    """

    def __init__(self, dic):
        # 'altmetric_id' is a required field in a citation
        if 'altmetric_id' in dic:
            for field, value in dic.items():
                setattr(self, field, value)
            stats = self.get_fields('title', 'doi', 'journal',
                                    'cited_by_posts_count', 'cited_by_tweeters_count',
                                    'cited_by_fbwalls_count', 'cited_by_gplus_count',
                                    'cited_by_rdts_count', 'cited_by_feeds_count')

            # replace '' with '0'
            for i in range(len(stats)):
                if not stats[i]:
                    stats[i] = '0'

            self.stats_all_posts=stats[3]
            self.stats_tweets=stats[4]
            self.stats_facebook=stats[5]
            self.stats_google_plus=stats[6]
            self.stats_reddit=stats[7]
            self.stats_blogs=stats[8]
        else:
            raise AltmetricException("Not a valid citation object")

    def get_fields(self, *args):
        """
        Returns a list containing values of the named fields in '*args'. 
        If named field does not exist, an empty string is returned to the list.
        """
        return [getattr(self, field, '') for field in args]

    def get_stats(self):
        stats = self.get_fields('title', 'doi', 'journal',
                                'cited_by_posts_count', 'cited_by_tweeters_count',
                                'cited_by_fbwalls_count', 'cited_by_gplus_count',
                                'cited_by_rdts_count', 'cited_by_feeds_count')

        # replace '' with '0'
        for i in range(len(stats)):
            if not stats[i]:
                stats[i] = '0'

        return dict(all_posts=stats[3], tweets=stats[4], facebook=stats[5], google_plus=stats[6],
                    reddit=stats[7], blogs=stats[8])

    def __repr__(self):
        stats = self.get_fields('title', 'doi', 'journal',
                                'cited_by_posts_count', 'cited_by_tweeters_count',
                                'cited_by_fbwalls_count', 'cited_by_gplus_count',
                                'cited_by_rdts_count', 'cited_by_feeds_count')

        # replace '' with '0'
        for i in range(len(stats)):
            if not stats[i]:
                stats[i] = '0'

        return ('Altmetrics on: "{0}" with doi {1} published in {2}.\n\n'
                '{3:11s} {4:>5}\n'
                '{5:11s} {6:>5}\n'
                '{7:11s} {8:>5}\n'
                '{9:11s} {10:>5}\n'
                '{11:11s} {12:>5}\n'
                '{13:11s} {14:>5}\n\n').format(stats[0], stats[1], stats[2],
                                               'All Posts', stats[3], 'Tweets', stats[4],
                                               'Facebook', stats[5], 'Google+', stats[6],
                                               'Reddit', stats[7], 'Blogs', stats[8])

# asl = AltmetricService()
# c = asl.get("10.1101/2020.04.23.055293")
#
# # a = Altmetric()
# # b = a.doi("10.1101/2020.04.23.055293")
# # c = Citation(b)
# print(c.stats_all_posts)
# print(c.stats_tweets)
# print(c.stats_facebook)
# print(c.stats_google_plus)
# print(c.stats_reddit)
# print(c.stats_blogs)