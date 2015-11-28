# coding: utf-8

from scrapy.downloadermiddlewares.retry import RetryMiddleware as BaseRetryMiddleware


class RetryMiddleware(BaseRetryMiddleware):

    def process_response(self, request, response, spider):
        response = super(RetryMiddleware, self).process_response(request, response, spider)
        if response.url.startswith('http://error.59store.com/'):
            return self._retry(request, response.meta['redirect_urls'][0], spider) or response
        return response
