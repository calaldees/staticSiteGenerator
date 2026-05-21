<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<%include file="_og_meta.mako"/>

	<title>TODO</title>
	<link id="favicon" rel="shortcut icon" type="image/png" href="data:image/png;base64,....==" />

	<link rel="stylesheet" href="/static/pure-min.css">
	<link rel="stylesheet" href="/static/grids-responsive-min.css">
	<link rel="stylesheet" href="/static/pure-layout-blog.css"/>

	<!--<link rel="stylesheet" href="/static/page.css"/>-->
	<script src="/static/static_site.js" async></script>
</head>
<body>

<%doc>-------------------------------------------------------------------</%doc>

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


<div id="layout" class="pure-g">

	<div class="sidebar pure-u-1 pure-u-md-1-4">
		<div class="header">
			<h1 class="brand-title">Title</h1>
			<h2 class="brand-tagline">Description</h2>
			<nav class="nav">
				<ul class="nav-list">
					<li class="nav-item"><a class="pure-button" href="/authors">Authors</a></li>
					<li class="nav-item"><a class="pure-button" href="/articles">Articles</a></li>
				</ul>
			</nav>
		</div>
	</div>

	<div class="content pure-u-1 pure-u-md-3-4">
		<div>
			<div class="posts">
				<h1 class="content-subhead">Pinned Post</h1>
				${render_post(db.get('articles/about'))}
			</div>

			<div class="posts">
				<h1 class="content-subhead">Recent Posts</h1>
				<%
				import datetime
				%>
				% for item in sorted(filter(lambda i: str(i['path_src']).startswith('article'), db.values()), key=lambda i: i.get('date',datetime.datetime.fromtimestamp(0, tz=datetime.UTC)), reverse=True)[:3]:
				${render_post(item)}
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
<%doc>-------------------------------------------------------------------</%doc>
</body>
</html>
