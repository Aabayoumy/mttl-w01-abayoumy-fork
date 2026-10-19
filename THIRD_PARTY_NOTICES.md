# Third-party notices / 제3자 라이선스 안내

이 도구는 Windows x64 로컬 테스트용입니다. 시스템 설치, 전역 PATH 변경, 레지스트리 등록, 기기 업로드 기능이 없습니다. 도구와 소스는 선택한 전용 폴더에서 관리합니다. 소스의 빌드 스크립트는 임의 코드를 실행할 수 있으므로 신뢰하는 소스만 사용하십시오.

`환경 준비`는 고정된 공식 URL에서 아래 구성 요소를 사용자 PC로 직접 다운로드하고 SHA-256을 확인합니다. 설치 관리자, npm, pip 또는 시스템 패키지 관리자를 실행하지 않습니다. 압축 파일의 링크와 폴더 밖 경로는 거부합니다. 다운로드 서버의 접근 로그에는 일반 다운로드와 마찬가지로 IP 등이 기록될 수 있습니다. 소스나 기기 설정을 업로드하지 않습니다.

## Downloads

- GNU Arm Embedded GCC 4.8.3-2014q1: Arduino 공식 다운로드 서버. GCC/Binutils의 GPL, 라이브러리 예외와 구성 요소별 라이선스가 적용됩니다. 컴파일러 사용 자체가 사용자 소스 전체에 GPL을 적용한다는 뜻은 아닙니다.
- Ameba Arduino SDK: Ameba-AIoT 공식 저장소의 커밋 `819d5a3252a4294847dc035bc431b1437dddbee3`. 공식 SDK 릴리스와 동일 커밋의 개별 파일 업데이트를 내려받습니다. 최상위 MIT 외에 Arduino LGPL, FreeRTOS 8.1.2 GPL+예외, Realtek 개별 고지가 혼재합니다. SDK를 사용하거나 수정 펌웨어를 배포할 때 해당 조건을 따로 검토해야 합니다.
- Python 3.12.10 embeddable: python.org. PSF 및 번들 구성 요소 라이선스.
- Node.js 22.14.0: nodejs.org. MIT 및 번들 구성 요소 라이선스.
- Unicorn 2.1.4: PyPI의 upstream wheel. 엔진 GPLv2 및 Python 바인딩 등의 개별 조건.
- Zopfli 0.4.3: PyPI. Apache-2.0 및 구성 요소 고지.
- Terser 5.44.0와 고정 버전 의존성: npm 공식 registry. BSD/MIT 등 각 패키지의 LICENSE.

정확한 URL, 버전, 크기와 SHA-256은 `dependencies.lock.json`에 기록되어 있습니다. 다운로드 캐시의 원본 archive와 추출된 LICENSE 파일을 보존합니다. 다운로드 방식을 사용한다고 완성 펌웨어의 라이선스 의무가 없어지는 것은 아닙니다.

## Builder EXE

EXE는 Python/Tcl/Tk를 포함하는 PyInstaller one-directory 패키지입니다. 동봉한 `licenses`와 `_internal`의 라이선스 파일을 유지하십시오. Python은 PSF, Tcl/Tk는 해당 고지, PyInstaller는 GPL+배포 예외 조건이 적용됩니다. EXE는 서명되지 않은 테스트 빌드입니다. Windows/보안 프로그램이 경고를 표시하면 확인 없이 실행하도록 우회하지 마십시오.

이 문서는 법률 검토를 대체하지 않습니다. 소스 공개가 제3자 코드 전체에 대한 새로운 라이선스 부여를 의미하지는 않습니다. 수정 펌웨어의 재배포 조건은 별도로 확인하십시오.

## English

This builder downloads pinned upstream toolchain/SDK/runtime packages directly to your PC, verifies hashes and extracts them into its own folder. It does not install system packages, change persistent PATH/environment/registry settings, or upload firmware or source. Reading third-party terms is required; downloading dependencies does not remove obligations on later firmware redistribution. Keep all upstream notices. The EXE is unsigned. Source publication does not grant a blanket license over third-party components.
