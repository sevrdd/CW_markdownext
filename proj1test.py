import mistletoe

print(1)

with open('foo.md', 'r') as fin:
    rendered = mistletoe.markdown(fin)
    print(rendered)
