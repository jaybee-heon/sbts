# [Docker](https://hub.docker.com/r/kimnaryeong/defects4j/tags)
### window
```bash
docker pull kimnaryeong/defects4j:after_init
docker run -it -v "$(Get-Location):/defects4j/" kimnaryeong/defects4j:after_init bash
```

### linux
```bash
docker pull kimnaryeong/defects4j:after_init
docker run -it -v $(pwd):/defects4j/ kimnaryeong/defects4j:after_init bash
```
* defects4j clone 후 defects4j 디렉토리에서 run
* docker 내부 변경 사항 로컬에도 저장됨  

# get_coverage.py
* defects4j 디렉토리에서 실행
* 참고하시라고 넣어놨어요

