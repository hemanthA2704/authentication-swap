from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
def body(remark):
    template = env.get_template("email_template.html")
    html_content = template.render(remark=remark)
    return html_content