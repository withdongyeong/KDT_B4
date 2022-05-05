# 프로그래머스 인공지능 데브코스 3기 최종 프로젝트

B4팀 조니조아아빠

김동영 : withdongyeong@gmail.com

# 프로젝트명 : 가나폰트(GAN Attribute font)

# 프로젝트 요약

사용자로부터 폰트에 대한 속성 10가지를 입력받아

(“예술적인”, “형식적인”, “우아한”, “현대적인”, “날카로운”, “부드러운”, “단단한”, “가독성있는”, “필기체”, “매력적인”)

1. [Attr2Font](https://github.com/hologerry/Attr2Font)(GAN)를 사용하여 입력된 속성 10가지로부터 36개의 glyph 이미지를 생성한다.
 
2. [dmfont](https://github.com/clovaai/fewshot-font-generation)(GAN)를 사용하여 36개의 glyph를 2,448개의 glyph 이미지 집합으로 확장한다.

3. `fontforge`를 사용하여 glyph 이미지 집합으로부터 .ttf(true type font) 파일을 생성한다.

Attribute의 사용자 입력과 생성된 .ttf 파일의 다운로드 서비스는 django를 통해 배포된 웹에서 이루어진다.
