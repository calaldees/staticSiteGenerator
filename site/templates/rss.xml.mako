<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
	<language>en-uk</language>
	<title>${site.title}</title>
	<link>${site.url}</link>
	<description>Free web building tutorials</description>
	<image>
		<url>${site.favicon}</url>
		<title>${site.title}</title>
		<link>${site.url}</link>
	</image>
	<pubDate>Thu, 27 Apr 2006</pubDate><%doc>latest pub date</%doc>
	<ttl>2880</ttl><%doc>Two days in minuets</%doc>

	% for article in db.articles:
	<item>
		<title>${article['title']}</title>
		<pubDate>${article['date']}</pubDate><%doc>Thu, 27 Apr 2006</%doc>
		<link>${article['path_dst']}</link>
		<description>${article['description']}</description>
		<author>${', '.join(article.get('authors', ()))}</author>
		<category></category>
		<%doc><enclosure url="https://www.w3schools.com/xml/rss.mp3" length="5000" type="audio/mpeg" /></%doc>
  	</item>
	% endfor

</channel>
</rss>