
all: svg2png mdtodoc

svg2png:
	cd images && sh convert_to_png.sh
	sed 's/\.svg/\.png/g' CHAPTER.md > CHAPTER_for_docx.md

mdtodoc:
	pandoc CHAPTER_for_docx.md -o "Serverless_PCA_Chapter.docx" --reference-doc=./reference.docx
	open Serverless_PCA_Chapter.docx
