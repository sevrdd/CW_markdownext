import mistletoe

flag_resize = "@@@"
resize_flag = False

md_content = []
img_var = []

with open('foo.md', 'r', encoding='utf-8') as fin: ## to add a var for the file name so it can be more dynamic
    literal_content = fin.read()
    # I KNOW ITS NOT ELEGANT LOL
    for word in literal_content.splitlines():
      if word.strip() == flag_resize:
        resize_flag = not resize_flag
      if resize_flag == True:
        img_var.append(word)
      md_content.append(word)
    print(img_var)
    print(md_content)

"""
<!DOCTYPE html>
<html>
<head>
<style>
html, body {
  height: 100%;
}

img.one {
  height: auto;
  width: auto;
}

img.two {
  height: 50%;
  width: 50%;
}
</style>
</head>
<body>

<h2>Set the height and width in %</h2>
<p>Resize the browser window to see the effect.</p>

<p>Original image:</p>
<img class="one" src="ocean.jpg" width="300" height="300"><br>

<p>Sized image (in %):</p>
<img class="two" src="ocean.jpg" width="300" height="300">

</body>
</html>
"""