from glob import glob
from jinja2 import Environment, FileSystemLoader
from markdown_toclify import markdown_toclify
from num2words import num2words
from os import devnull, mkdir, path
from re import DOTALL, finditer, search, sub
from shutil import rmtree
from subprocess import CalledProcessError, check_output

posts_dir = path.dirname(__file__)
root_dir = path.dirname(posts_dir)
build_dir = path.join(posts_dir, 'build')
template_dir = path.join(posts_dir, 'templates')

rmtree(build_dir, ignore_errors=True)
mkdir(build_dir)

def run_bash(command_as_tuple):
    readable_command = ' '.join(command_as_tuple)
    output = "$ %(readable_command)s\n" % locals()
    output += check_output(command_as_tuple)
    return output

def include_with_default(current_tag, relative_path, language):
    language = language or path.splitext(path.basename(relative_path))[1].replace('.', '')
    new_include = "```%(language)s\n" % locals()
    try:
        new_include += check_output(
            ['git', 'show', current_tag + ':' + relative_path],
             stderr=open(devnull, 'w')
        )
    except CalledProcessError:
        with file(path.join(root_dir, relative_path), 'r') as file_to_include:
            new_include += file_to_include.read()
    new_include += '```\n'
    return new_include

jinja_env = Environment(
    loader=FileSystemLoader( template_dir )
)

jinja_env.globals['include_with_default'] = include_with_default
jinja_env.globals['num2words'] = num2words
jinja_env.globals['run_bash'] = run_bash

for post_filename in glob(path.join(template_dir, 'post-*.j2')):
    post_basename = path.basename(post_filename)
    template = jinja_env.get_template(post_basename)
    post_basename = post_basename.replace('.j2', '')
    pre_toc = template.render(
        post_number=int(post_basename.split('-')[1]),
        current_tag=path.splitext(post_basename)[0]
    )
    output_filename = path.join(build_dir, post_basename.replace('.j2', ''))
    with file(output_filename, 'w+') as built_file:
        built_file.write(sub(r'\n\n```\n\n', '\n```\n\n', pre_toc))
        built_file.seek(0)
        built_file.write(sub(r'\n\n+', '\n\n', markdown_toclify(
            input_file=output_filename,
            github=True,
            no_toc_header=True,
            placeholder='<!-- markdown_toclify -->',
            exclude_h=[1]
        )))
        built_file.seek(0)
        file_contents = built_file.read()
        built_file.seek(0)
        full_toc = search(r'<p class="nav-p"><a id="post-nav"></a></p>\s+(-.*?)\n\r?\n\r?', file_contents, DOTALL)
        if full_toc:
            new_toc = full_toc.group()
            for dashed_slug in finditer(r'(?:\(#)[a-z\-]+(?:\))', new_toc):
                new_toc = new_toc.replace(
                    dashed_slug.group(),
                    dashed_slug.group().replace('-', '')
                )
            built_file.write(file_contents.replace(full_toc.group(), new_toc))




