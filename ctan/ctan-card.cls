\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ctan-card}[2026/08/21 CTAN card class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage{fontspec}
\RequirePackage{xeCJK}
\RequirePackage{hyperref}
\RequirePackage{tabularx}
\RequirePackage{collcell}
\RequirePackage{xurl}

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

\setlength{\textwidth}{210mm}
\setmainfont{MonaspiceNe NFM}
\setCJKmainfont{Sarasa Mono SC}

\definecolor{fg}{HTML}{000000}

\hypersetup{colorlinks=true, linkcolor=fg, urlcolor=fg}
\urlstyle{same}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\setlength{\fboxsep}{10pt}
\setlength{\fboxrule}{1pt}

\newlength{\ctan@imgheight}
\newlength{\ctan@txtblockheight}
\newlength{\ctan@labelwidth}
\newlength{\ctan@colongap}
\newlength{\ctan@colonwidth}
\newlength{\ctan@colsep}
\newlength{\ctan@hmargin}
\newlength{\ctan@vmargin}

% Label column: strip the trailing colon, right-align the label in a fixed
% width box, and place the colon in a zero-width rlap so it sits one space
% width to the right of the label text.  The source remains "Label: & value".
\newcommand{\ctan@formatlabel}[1]{%
  \ctan@formatlabel@aux#1:\@nil
}
\def\ctan@formatlabel@aux#1:#2\@nil{%
  \makebox[\ctan@labelwidth][r]{#1\rlap{\kern\ctan@colongap:}}%
}
\newcolumntype{L}{>{\collectcell\ctan@formatlabel}r<{\endcollectcell}}

\RequirePackage[paperwidth=210mm,paperheight=1200pt,margin=0pt]{geometry}

% Per-card data.  Each .tex file redefines these two macros.
\providecommand{\CardImage}{}
\providecommand{\CardRows}{}

\AtBeginDocument{\fontsize{8pt}{10pt}\selectfont}

\newcommand{\makectancard}{%
  % Compute layout parameters in the current (7pt) font.
  \setlength{\ctan@colongap}{\fontdimen2\font}%
  \settowidth{\ctan@labelwidth}{Maintainer}%
  \settowidth{\ctan@colonwidth}{:}%
  \setlength{\ctan@colsep}{\dimexpr2\ctan@colongap+\ctan@colonwidth\relax}%
  \setlength{\ctan@hmargin}{29pt}% page edge to frame outer edge -> white fill 30pt from edge
  \setlength{\ctan@vmargin}{29pt}% page edge to frame outer edge -> white fill 30pt from edge
  % Measure the natural height of the background image.
  \setbox2=\hbox{\ctan@includeimage[width=\textwidth]{\CardImage}}%
  \setlength{\ctan@imgheight}{\ht2}%
  % Measure the text block so we know how much space to reserve at the bottom.
  \setbox3=\vbox{%
    \hsize=\textwidth
    \vspace*{\ctan@vmargin}%
    \noindent\hbox{%
      \kern\ctan@hmargin%
      \fcolorbox{black}{white}{%
        \begin{tabularx}{\dimexpr\textwidth-80pt\relax}{@{}L@{\hspace{\ctan@colsep}}X@{}}%
          \CardRows
        \end{tabularx}%
      }%
      \kern\ctan@hmargin%
    }%
    \vspace*{\ctan@vmargin}%
  }%
  \setlength{\ctan@txtblockheight}{\dimexpr\ht3+\dp3\relax}%
  % Compose the final page: full image with the text block overlaid at the
  % bottom.  The old implementation included the image a second time and clipped
  % it with \clipbox; that caused some vector PDF backgrounds to have their
  % internal line spacing squeezed.  We now use an invisible strut with the same
  % vertical footprint as the clipped image to keep the layout math identical
  % while only including the background once.
  \setbox0=\vbox to \ctan@imgheight{%
    \hsize=\textwidth
    \noindent\ctan@includeimage[width=\textwidth]{\CardImage}\par
    \nointerlineskip
    \kern-\dimexpr\ctan@imgheight\relax
    \noindent\rule[\dimexpr\ctan@txtblockheight-\ctan@imgheight\relax]{\textwidth}{0pt}\par
    \nointerlineskip
    \vspace*{\ctan@vmargin}%
    \noindent\hbox{%
      \kern\ctan@hmargin%
      \fcolorbox{black}{white}{%
        \begin{tabularx}{\dimexpr\textwidth-80pt\relax}{@{}L@{\hspace{\ctan@colsep}}X@{}}%
          \CardRows
        \end{tabularx}%
      }%
      \kern\ctan@hmargin%
    }%
    \vspace*{\ctan@vmargin}%
  }%
  \pdfpageheight=\ctan@imgheight
  \box0
}
