============
mdx_sections
============

Overview
========

This module is an extension to `Python-Markdown <https://github.com/waylan/Python-Markdown>`_ which provides the ability to add a small amount of structure to your Markdown documents.

There are two premises underlying the operation of this extension:

- Each heading element indicates the start of a new document section.
- Document sections can be nested, and the parent of a document section is the section created by the first preceding heading element with a higher order *e.g.* an ``h2`` section is contained by the heading block appearing prior to it which corresponds to an ``h1``. If there is no such element, then it is a child of the root element.

The new section (a containing ``div`` element) can be configured to have an specific ``id`` and ``class`` attribute. The syntax is::

  # {id,class} Title

Both ``id`` and ``class`` are optional, the contaaining ``div`` element will always be created as long as this extension is enabled.

One example should make this clear. Suppose the following input document is provided::
  
    # {resume} Resum&eacute;
    
    ## {education} Education
    Educational experience
    
    ## {experience} Working Experience
    Work experience
    
    ### {xyz_corp,employer} XYZ Corp.
    I worked at XYZ
    
    ### {acme_inc,employer} Acme Inc.
    I also worked at Acme
    
    ## Hobbies
    - Cards
    - Books
    - Dogs
    
    ### About _my_ hobbies
    My hobbies are great.

This would transform to become::

    <div class="section" id="section_resume">
      <h1 class="title">Resum&eacute;</h1>
      <div class="section" id="section_education">
        <h2 class="title">Education</h2>
        <p>Educational experience</p>
      </div>
      <div class="section" id="section_experience">
        <h2 class="title">Working Experience</h2>
        <p>Work experience</p>
        <div class="employer" id="section_xyz_corp">
          <h3 class="title">XYZ Corp.</h3>
          <p>I worked at XYZ</p>
        </div>
        <div class="employer" id="section_acme_inc">
          <h3 class="title">Acme Inc.</h3>
          <p>I also worked at Acme</p>
        </div>
      </div>
      <div class="section">
        <h2 class="title">Hobbies</h2>
        <ul>
          <li>Cards</li>
          <li>Books</li>
          <li>Dogs</li>
        </ul>
        <div class="section">
          <h3 class="title">About <em>my</em> hobbies</h3>
          <p>My hobbies are great.</p>
        </div>
      </div>
    </div>

The resulting document is, IMO, semantically correct. It's also easier to style with CSS.

Installation
============

Install using setuptools, e.g. (within a virtualenv)::

    $ pip install mdx_sections

Or if you prefer to get the latest from Github::

    $ git clone git://github.com/jessedhillon/mdx_sections.git

Usage
=====

For an extended introduction to Python-Markdown extensions, see `the documentation http://freewisdom.org/projects/python-markdown/Extensions`.

This extension is available by the short name of ``sections``, and it has two config parameters:

- ``section_cls``,  defaults to ``section``. This is the default CSS class applied to a generated ``div``, when the Markdown document does not specify one.
- ``heading_cls``,  defaults to ``title``. This is the default CSS class applied to the ``h[1-6]`` element which is being transformed.
