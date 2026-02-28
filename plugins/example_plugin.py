def register(registry):
    def hello(args, ctx):
        msg = args.strip().strip('"') or "plugin"
        print(f"[plugin] {msg}")
        return msg

    registry.register("plugin.hello>", hello)
