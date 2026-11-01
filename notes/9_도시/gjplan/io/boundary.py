"""구역 경계 읽기.

SHP 권장. ezdxf는 DXF만 읽으므로 DWG는 Rhino/QGIS로 변환하거나
국토정보플랫폼에서 SHP로 받는다.

레이어 규약: BOUNDARY(닫힌 폴리라인 1개), FIXED_*, ANCHOR_*(선택)
"""

CRS_TARGET = "EPSG:5187"  # Korea 2000 동부원점


def load_boundary(path: str, layer: str = "BOUNDARY"):
    """경계 폴리곤을 읽어 EPSG:5187로 변환해 반환한다.

    면적을 즉시 출력한다 — 좌표계 오류는 여기서 잡는다.
    """
    raise NotImplementedError("구현 순서 1~2주차. gjplan/README.md 참조")
