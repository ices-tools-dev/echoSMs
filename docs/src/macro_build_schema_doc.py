def define_env(env):
    # Variables are accessible as {{ version }} in templates
    env.variables["version"] = "1.0"

    # Macros are called as {{ greet("World") }}
    @env.macro
    def schema_doc(name):
        return 'ABCDEFG'

    # Filters are applied as {{ "hello" | shout }}
    @env.filter
    def shout(text):
        return text.upper()
