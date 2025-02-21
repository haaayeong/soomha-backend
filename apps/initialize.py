from apps.crud.models import db, Level

def initialize_levels():
  if Level.query.count() == 0:
    levels = [
      Level(name="어린이", required_stamps=0),
      Level(name="탐험가", required_stamps=5),
      Level(name="지킴이", required_stamps=10),
      Level(name="대장", required_stamps=15),
      Level(name="마스터", required_stamps=20)
    ]

    db.session.add_all(levels)
    db.session.commit()
    print("레벨 데이터 초기화 완료!")