from conan.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(archs=["x86_64"])
    # builder.add_common_builds(shared_option_name="m4:shared")

    # filtered_builds = []
    # for settings, options, env_vars, build_requires in builder.builds:
    #     if settings["build_type"] == "Release":
    #         filtered_builds.append([settings, options, env_vars, build_requires])
    # builder.builds = filtered_builds


    builder.run()
