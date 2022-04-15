# 프로그래머스 인공지능 데브코스 3기 최종 프로젝트

B4팀

김동영 : withdongyeong@gmail.com

# 프로젝트명 : 미정

# 프로젝트 요약

사용자로부터 폰트에 대한 속성 37가지를 입력받아

1. `Attr2Font(GAN)`를 사용하여 입력된 속성 37가지로부터 52개의 glyph 이미지를 생성한다.
 
2. `dmfont(GAN)`를 사용하여 52개의 glyph를 약 2400개 이상의 glyph 이미지 집합으로 확장한다.

3. `fontforge`를 사용하여 glyph 이미지 집합으로부터 .ttf(true type font) 파일을 생성한다.

Attribute의 사용자 입력과 생성된 .ttf 파일의 다운로드 서비스는 django를 통해 배포된 웹에서 이루어진다.
