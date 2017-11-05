import ast, glob, os, re, subprocess

# Specify a few important directories
post_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(post_dir)
provisioning_dir = os.path.join(post_dir, '..', 'provisioning')

# Common regex flags
generic_flags = re.IGNORECASE | re.DOTALL

# TODO: Is regex compilation necessary?

# Specify the pattern for a bash block
bash_block_regex = r'(<!--\s+wotw-build-bash\s+(.*?)\s*?\n\s*-->)(\s*```.*?```)?\s*(?:\n\r?)'
bash_block_pattern = re.compile(bash_block_regex, generic_flags)

# TODO: DRY this up a bit
# TODO: learn how to reuse raw strings

# Specify the TOC pattern
series_toc_regex = r'(<!--\s+wotw-series-toc\s+-->\n\r?).*?(\n?\r?<!--\s+/wotw-series-toc\s+-->)\s*'
series_toc_pattern = re.compile(series_toc_regex, generic_flags)

# Specify the repo link pattern
repo_link_regex = r'(<!--\s+wotw-repo-link\s+-->\n\r?).*?(\n?\r?<!--\s+/wotw-repo-link\s+-->)\s*'
repo_link_pattern = re.compile(repo_link_regex, generic_flags)

# Specify the file include pattern
include_regex = r'(<!--\s+wotw-include-file\s+filename:\s*(.*?)(\s+language:\s*(.*?))?\s+-->)(\s*\[.*?:)?(\s*```.*?```)?\s*(?:\n\r?)'
include_pattern = re.compile(include_regex, generic_flags)

def compile_bash(contents):
    """Compile any found bash references

    Keyword arguments:
    contents -- post contents to update
    """
    for found_block in re.finditer(bash_block_pattern, contents):
        original_block = found_block.group()
        new_block = found_block.group(1)
        new_block += os.linesep
        new_block += '```'
        working_directory = os.getcwd()
        os.chdir(root_dir)
        for masked_command_to_run in found_block.group(2).split('\n'):
            command_to_run = ast.literal_eval(masked_command_to_run)
            readable_command = ' '.join(command_to_run)
            command_output = subprocess.check_output(command_to_run)
            new_block += os.linesep
            new_block += "$ %(readable_command)s" % locals()
            new_block += os.linesep
            new_block += command_output
        os.chdir(working_directory)
        new_block += '```'
        new_block += os.linesep + os.linesep
        contents = contents.replace(original_block, new_block)
    return contents

def update_series_toc(contents):
    """Refresh the TOC

    Keyword arguments:
    contents -- post contents to update
    """
    with file(os.path.join(post_dir, 'series-toc.md'), 'r') as series_toc:
        toc_contents = series_toc.read()
        contents = re.sub(series_toc_pattern, r'\1' + toc_contents.strip() + r'\2\n\n', contents)
    return contents

def update_repo_link(post_filename, contents):
    """Refresh the repo link

    Keyword arguments:
    post_filename -- The post filename, whose basename minus extension is used as the git tag
    contents -- post contents to update
    """
    with file(os.path.join(post_dir, 'repo-link.md'), 'r') as repo_link:
        repo_link_contents = repo_link.read()
        repo_link_contents = repo_link_contents.replace('~replace-me~', os.path.basename(os.path.splitext(post_filename)[0]))
        contents = re.sub(repo_link_pattern, r'\1' + repo_link_contents.strip() + r'\2\n\n', contents)
    return contents

def compile_includes(post_filename, contents):
    """Load local includes from the proper revision. Defaults to the current working tree.

    Keyword arguments:
    post_filename -- The post filename, whose basename minus extension is used as the git tag
    contents -- post contents to update
    """
    current_tag = os.path.basename(os.path.splitext(post_filename)[0])
    repo_root = '//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/'
    repo_root += current_tag
    repo_root += '/'
    for found_include in re.finditer(include_pattern, contents):
        original_include = found_include.group()
        relative_path = found_include.group(2)
        new_include = found_include.group(1)
        new_include += os.linesep
        new_include += '[`' + relative_path + '`](' + repo_root + relative_path + '):'
        new_include += os.linesep
        new_include += '```'
        if found_include.group(4):
            new_include += found_include.group(4)
        else:
            new_include += os.path.splitext(relative_path)[1].replace('.', '')
        new_include += os.linesep
        try:
            new_include += subprocess.check_output(['git', 'show', current_tag + ':' + relative_path], stderr=open(os.devnull, 'w'))
        except subprocess.CalledProcessError:
            with file(os.path.join(root_dir, relative_path), 'r') as file_to_include:
                new_include += file_to_include.read()
        new_include += '```'
        new_include += os.linesep + os.linesep
        contents = contents.replace(original_include, new_include)
    return contents

def compile_post(post_filename):
    """Compiles a single post.

    Keyword arguments:
    post_filename -- The path to the post to compile
    """
    with file(post_filename, 'r+') as post_to_compile:
        post_contents = post_to_compile.read()
        post_contents = update_series_toc(post_contents)
        post_contents = update_repo_link(post_filename, post_contents)
        post_contents = compile_bash(post_contents)
        post_contents = compile_includes(post_filename, post_contents)
        post_to_compile.seek(0)
        post_to_compile.truncate()
        post_to_compile.write(post_contents)

def compile_all_posts():
    """Compiles all the posts"""
    for post_file in glob.glob(os.path.join(post_dir, 'post-*.md')):
        compile_post(post_file)

# Compile all the things
compile_all_posts()
