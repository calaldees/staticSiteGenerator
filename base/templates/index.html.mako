<%
from itertools import islice
%>
<%include file="_head.mako"/>

<%def name="render_post(item)">
	<%
		author_name = next(iter(item.get('authors',())), '')
		author = db.get(f'authors/{author_name.lower().replace(" ","-")}')
		title = item['title']
		description = item['description']
		a_href = item['path_dst']
	%>
	<section class="post">
		<header class="post-header">
			<a href="${author.get('path_dst')}">
			<img width="48" height="48" alt="${author_name}" class="post-avatar" src="${author.get('gravatar_url') or 'placeholder'}">
			</a>
			<a href="${a_href}">
			<h2 class="post-title">${title}</h2>
			</a>
			<p class="post-meta">
				By <a href="${author.get('path_dst')}" class="post-author">${author_name}</a>
				under
				% for category in item.get('categories', ()):
					<a class="post-category post-category-design" href="#">${category}</a>
				% endfor
				${item.get('date', '')}
			</p>
		</header>
		<div class="post-description">
			<p>${description}</p>
		</div>
	</section>
</%def>

<body>
<div id="layout" class="pure-g">
	<%include file="_nav.mako"/>

	<div class="content-wrapper pure-u-1 pure-u-md-3-4">
		<div class="content">

			<div class="posts">
				<h1 class="content-subhead">Pinned Post</h1>
				% for article_name in index.pinned_articles:
				${render_post(db.get(article_name))}
				% endfor
			</div>

			<div class="posts">
				<h1 class="content-subhead">Recent Posts</h1>
				% for article in islice(db.articles, 3):
				${render_post(article)}
				% endfor
			</div>

			<div class="footer">
				<div class="pure-menu pure-menu-horizontal">
					<ul>
						<li class="pure-menu-item"><a href="http://purecss.io/" class="pure-menu-link">About</a></li>
						<li class="pure-menu-item"><a href="http://github.com/pure-css/pure/" class="pure-menu-link">GitHub</a></li>
					</ul>
				</div>
			</div>

		</div>
	</div>

</div>
</body>
</html>
