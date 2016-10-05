# coding:utf-8

import re
from urlparse import urljoin

from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware as BaseRedirectMiddleware

class RedirectMiddleware(BaseRedirectMiddleware):

    def process_response(self, request, response, spider):
        if request.meta.get('dont_redirect', False) or request.method == 'HEAD' or \
                not isinstance(response, HtmlResponse):
            return response

        if isinstance(response, HtmlResponse):
            match = re.match(r"<script>location.href='(.*)'\s*</script>", response.body)
            if match is not None:
                redirected_url = urljoin(request.url, match.group(1))
                redirected = self._redirect_request_using_get(request, redirected_url)
                return self._redirect(redirected, request, spider, response.status)

        return response
