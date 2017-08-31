import os
from setuptools import setup



def package_data(pkg, root_list):
    """ Generic function to find package_data for 'pkg' under 'root'. """
    data = []
    for root in root_list:
        for dirname, _, files  in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}

BLOCKS = [
    'template_builder = template_builder.mentoring:TemplateBlock',
    'tb-fancy = template_builder.mentoring:FancyXBlock',
    'tb-question-answer = template_builder.mentoring:QuestionAnswerXBlock',
    'tb-question-generator = template_builder.question_generator_block:QuestionGeneratorXBlock',
    ]


setup(
    name='xblock-question-builder',
    version='1.0.0',
    description='Xblock - Question Template Builder',
    packages=['template_builder'],
    install_requires=[
        'XBlock',
        'xblock-utils',
    ],
    entry_points={
        'xblock.v1' : BLOCKS,
    },
    package_data=package_data("template_builder", ["templates", "public", "migrations", "static"]),
)



