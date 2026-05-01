import frontmatter


if __name__ == '__main__':
    post = frontmatter.load('./content/test.md')
    print(post.metadata)
