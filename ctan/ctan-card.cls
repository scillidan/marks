\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ctan-card}[2026/08/21 CTAN card class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage{adjustbox}
\RequirePackage{fontspec}
\RequirePackage{xeCJK}
\RequirePackage{hyperref}
\RequirePackage{tabularx}
\RequirePackage{xurl}

% The build script writes this file to tell us where the background images live.
\IfFileExists{_output/imgdir.tex}{\input{_output/imgdir.tex}}{\providecommand{\CDNImageDir}{}}
\graphicspath{{\CDNImageDir}}

% Keep a reference to the original \includegraphics in case a build-time patch
% redefines it, and provide a helper that strips the extension so a .tex file
% can say "archivo.jpg" while the actual asset is "archivo.pdf"/".png".
\let\ctan@orig@includegraphics\includegraphics
\newcommand{\ctan@includeimage}[2][]{%
  \begingroup
    \edef\ctan@imgarg{#2}%
    \expandafter\filename@parse\expandafter{\ctan@imgarg}%
    \ctan@orig@includegraphics[#1]{\filename@area\filename@base}%
  \endgroup
}

\setlength{\textwidth}{148mm}
\setmainfont{MonaspiceNe NFM}
\setCJKmainfont{Sarasa Mono SC}

\definecolor{fg}{HTML}{000000}

\hypersetup{colorlinks=true, linkcolor=fg, urlcolor=fg}
\urlstyle{same}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\fboxsep}{5pt}
\setlength{\fboxrule}{1pt}

\newlength{\ctan@imgheight}
\newlength{\ctan@txtblockheight}

\RequirePackage[paperwidth=148mm,paperheight=1200pt,margin=0pt]{geometry}

% Per-card data.  Each .tex file redefines these two macros.
\providecommand{\CardImage}{}
\providecommand{\CardRows}{}

\AtBeginDocument{\fontsize{6pt}{7.2pt}\selectfont}

\newcommand{\makectancard}{%
  % Measure the natural height of the background image.
  \setbox2=\hbox{\ctan@includeimage[width=\textwidth]{\CardImage}}%
  \setlength{\ctan@imgheight}{\ht2}%
  % Measure the text block so we know how much of the image to clip.
  \setbox3=\vbox{%
    \hsize=\textwidth
    \vspace*{5pt}%
    \noindent\hbox{%
      \kern5pt%
      \fcolorbox{black}{white}{%
        \begin{tabularx}{\dimexpr\textwidth-22pt\relax}{@{}r@{\hspace{8pt}}X@{}}%
          \CardRows
        \end{tabularx}%
      }%
      \kern5pt%
    }%
    \vspace*{5pt}%
  }%
  \setlength{\ctan@txtblockheight}{\dimexpr\ht3+\dp3\relax}%
  % Compose the final page: full image, then a clipped copy with the text block
  % overlaid at the bottom.  Links are built inline here (not reused from box3).
  \setbox0=\vbox to \ctan@imgheight{%
    \hsize=\textwidth
    \noindent\ctan@includeimage[width=\textwidth]{\CardImage}\par
    \nointerlineskip
    \kern-\dimexpr\ctan@imgheight\relax
    \noindent\clipbox{0 0 0 \ctan@txtblockheight}{\ctan@includeimage[width=\textwidth]{\CardImage}}\par
    \nointerlineskip
    \vspace*{5pt}%
    \noindent\hbox{%
      \kern5pt%
      \fcolorbox{black}{white}{%
        \begin{tabularx}{\dimexpr\textwidth-22pt\relax}{@{}r@{\hspace{8pt}}X@{}}%
          \CardRows
        \end{tabularx}%
      }%
      \kern5pt%
    }%
    \vspace*{5pt}%
  }%
  \pdfpageheight=\ctan@imgheight
  \box0
}
