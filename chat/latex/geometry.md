> The package provides an easy and flexible user interface to customize page layout, implementing auto-centering and auto-balancing mechanisms so that the users have only to give the least description for the page layout. For example, if you want to set each margin 2cm without header space, what you need is just \usepackage[margin=2cm,nohead]{geometry}.  
> The package knows about all the standard paper sizes, so that the user need not know what the nominal ‘real’ dimensions of the paper are, just its standard name (such as a4, letter, etc.).  
> An important feature is the package’s ability to communicate the paper size it’s set up to the output (whether via DVI \specials or via direct interaction with pdf(La)TeX). [ctan.org/pkg/geometry]

译：该包提供了一个简单灵活的用户界面，用于自定义页面布局，采用自动居中和自动平衡机制，使用户只需提供最少的页面布局描述即可。例如，如果你想将每个边距设置为2厘米且不留头部空间，你只需使用`\usepackage[margin=2cm,nohead]{geometry}`。  
该包了解所有标准纸张尺寸，因此用户无需知道纸张的名义“真实”尺寸，只需知道其标准名称（如a4、letter等）。  
一个重要的特性是该包能够将其设置的纸张尺寸传达给输出（无论是通过DVI的`\specials`还是通过与pdf(La)TeX的直接交互）。