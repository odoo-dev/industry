def _disable_view(env):
    env.ref("website.template_header_default").active = False
    env.ref("website.template_header_boxed").active = True
    env.ref("website.header_navbar_pills_style").active = True
    print("______________________________________\n")