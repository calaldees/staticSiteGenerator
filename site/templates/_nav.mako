<div class="header pure-u-1 pure-u-md-1-4">
    ## sidebar
    ## <div class="header">
        <a href="/">
            <img src="${site.logo}" alt="${site.title} logo" class="pure-img">
            <h1 class="brand-title">${site.title}</h1>
            <h2 class="brand-tagline">${site.tagline}</h2>
        </a>
        <nav class="nav">
            <ul class="nav-list">
                % for nav_item in navigation:
                <li class="nav-item"><a class="pure-button" href="${nav_item['path']}">${nav_item['name']}</a></li>
                % endfor
            </ul>
        </nav>
    ## </div>
</div>

<%doc>
https://github.com/pure-css/pure/blob/main/site/static/layouts/side-menu/index.html
<a href="#menu" id="menuLink" class="menu-link"><span></span></a>
<div id="menu">
    <div class="pure-menu">
        <a class="pure-menu-heading" href="/">ComputingTeachers.uk</a>
        <ul class="pure-menu-list">
            <% menu = ('articles', 'authors') %>
            % for menu_item in menu:
            <%
                selected = 'menu-item-divided pure-menu-selected' if metadata and str(metadata.path_dst).startswith(menu_item) else ''
            %>
            <li class="pure-menu-item ${selected}">
                <a href="/${menu_item}" class="pure-menu-link">${menu_item.title()}</a>
            </li>
            % endfor
        </ul>
    </div>
</div>
</%doc>