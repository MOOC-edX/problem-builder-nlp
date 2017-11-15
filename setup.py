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
    'problem-template-builder = problem_template_builder.mentoring:TemplateBuilderContainerBlock',
    'tb-math-problem-template-builder = problem_template_builder.math_problem_template_builder:MathProblemTemplateBuilderXBlock',
    ]


setup(
    name='xblock-problem-template-builder',
    version='1.0.0',
    description='Xblock - Problem Template Builder using Nature Language Processing',
    packages=['problem_template_builder'],
    install_requires=[
        'XBlock',
        'xblock-utils',
    ],
    entry_points={
        'xblock.v1' : BLOCKS,
    },
    package_data=package_data("problem_template_builder", ["static"]),
)



