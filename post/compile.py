import ast, glob, os, re, subprocess

post_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(post_dir)
provisioning_dir = os.path.join(post_dir, '..', 'provisioning')

generic_flags = re.IGNORECASE | re.DOTALL

bash_block_regex = r'<!--\s+wotw-build-bash\s+(.*?)\s+/wotw-build-bash\s+-->\s*```(\w+)?(.*?)```'
bash_block_pattern = re.compile(bash_block_regex, generic_flags)

# TODO: DRY this up a bit
# TODO: learn how to reuse raw strings
series_toc_regex = r'(<!--\s+wotw-series-toc\s+-->\n\r?).*?(\n?\r?<!--\s+/wotw-series-toc\s+-->)\s*'
series_toc_pattern = re.compile(series_toc_regex, generic_flags)

repo_link_regex = r'(<!--\s+wotw-repo-link\s+-->\n\r?).*?(\n?\r?<!--\s+/wotw-repo-link\s+-->)\s*'
repo_link_pattern = re.compile(repo_link_regex, generic_flags)

include_regex = r'(<!--\s+wotw-include-file\s+filename:\s*(.*?)(\s+language:\s*(.*?))?\s+-->)(\s*\[.*?:)?(\s*```.*?```)?\s*(?:\n\r?)'
include_pattern = re.compile(include_regex, generic_flags)

def compile_bash(contents):
    for found_block in re.finditer(bash_block_pattern, contents):
        original_block = found_block.group()
        output = ''
        os.chdir(root_dir)
        for masked_command_to_run in found_block.group(1).split('\n'):
            command_to_run = ast.literal_eval(masked_command_to_run)
            readable_command = ' '.join(command_to_run)
            command_output = subprocess.check_output(command_to_run)
            output += os.linesep
            output += "$ %(readable_command)s" % locals()
            output += os.linesep
            output += command_output
        os.chdir(post_dir)
        updated_block = original_block.replace(found_block.group(3), output)
        contents = contents.replace(original_block, updated_block)
    return contents

def update_series_toc(contents):
    with file(os.path.join(post_dir, 'series-toc.md'), 'r') as series_toc:
        toc_contents = series_toc.read()
        contents = re.sub(series_toc_pattern, r'\1' + toc_contents.strip() + r'\2\n\n', contents)
    return contents

def update_repo_link(post_filename, contents):
    with file(os.path.join(post_dir, 'repo-link.md'), 'r') as repo_link:
        repo_link_contents = repo_link.read()
        print repo_link_contents
        repo_link_contents = repo_link_contents.replace('~replace-me~', os.path.basename(os.path.splitext(post_filename)[0]))
        print repo_link_contents
        contents = re.sub(repo_link_pattern, r'\1' + repo_link_contents.strip() + r'\2\n\n', contents)
        print contents
    return contents

def compile_includes(post_filename, contents):
    repo_root = '//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/'
    repo_root += os.path.basename(os.path.splitext(post_filename)[0])
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
        with file(os.path.join(root_dir, relative_path), 'r') as file_to_include:
            new_include += file_to_include.read()
        new_include += '```'
        new_include += os.linesep + os.linesep
        contents = contents.replace(original_include, new_include)
    return contents

def compile_post(post_filename):
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
    for post_file in glob.glob(os.path.join(post_dir, 'post-*.md')):
        compile_post(post_file)

compile_all_posts()

# compile_post(os.path.join(post_dir, 'sample.md'))
