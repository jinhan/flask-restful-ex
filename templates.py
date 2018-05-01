text_templates = {
	1: '#{custom1} #{custom2} #{custom3}',

	2: '2018년 6월 13일 오전 7시부터 제7대 전국동시지방선거가 막을 열었다. 오후 6시를 기준으로 투표가 마감되었고, 최종 집계된 투표율은 {toorate_avg_nat}%로 나타났다.',

	3: '이번 지방선거의 투표율은 지난 선거에 비해 {current_toorate_past_toorate}%p {toorate_compare} 것으로, {toorate_compare_add}. 전국에서 가장 투표율이 높은 지역은 {toorate_rank1}이며, 그 뒤를 {toorate_rank}{josa} 뒤따르고 있다.',
	# 투표진행중일때는?

	4: '{region1} 지역 전체의 투표율은 {toorate_region1}%로 전국 평균보다 약 {toorate_region1_toorate_avg_nat}% 포인트 {toorate_compare1} 수치이며, {region2}는 {toorate_region2}%로 전국 평균보다 약간 {toorate_compare2} 투표율을 보였다.',

	5: '{hour} 현재 전국 평균 개표율은 {openrate_avg_nat}%이며, 서울은 {openrate_seoul}%, 경기도는 {openrate_gyeonggi}%의 개표 진행 상황을 보이고 있다.',

	6: '{hour} 현재 전국에서 가장 개표가 빠른 지역은 {openrate_sunname1_rank1}이며, 시군구 단위에서 개표가 가장 빠른 곳은 {openrate_sunname2_rank1}로 {openrate_sunname2_rank1_rate}%의 개표율을 보이고 있다.',

	7: '{hour} 현재 {region1} 지역 전체의 개표율은 {openrate_region1}%로 {region1_exception} {region2}는 {openrate_region2}%로 {region2_exception}',
	'7-0': '아직 개표가 시작되지 않았다.',
	'7-1': '전국 평균보다 약 {openrate_region1_openrate_avg_nat}% 포인트 {compare_region1} 수치이며,',
	'7-2': '전국 평균보다 {compare_region2} 개표율을 보였다.',

	8: '{hour} 현재 총 {num}개의 지방자치단체장 및 지방자치 의원을 선출하는 이번 지방 선거에서 {rank1_party}은 {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}({rank2_party_num}개), {rank3_party}({rank3_party_num}개){josa} 잇고 있다.',

	9: '{hour} 현재 전국 {num}개의 시/도지사 선거에서 {rank1_party}은 {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}({rank2_party_num}개), {rank3_party}({rank3_party_num}개){josa} 잇고 있다.',

	10: '{hour} 현재 {region1}{sido_type} 선거에서는 {openrate_region1}%의 개표율을 보이는 가운데 {region1_rank1_party} {region1_rank1_candidate} 후보가 {region1_rank1_pollrate}%의 득표율로 1위, {region1_rank2_party} {region1_rank2_candidate} 후보가 {region1_rank2_pollrate}%의 득표율로 2위를 달리고 있다.',

	11: '{hour} 현재 {region2}{sido_type} 선거에서는 {openrate_region2}%의 개표율을 보이는 가운데 {region2_rank1_party} {region2_rank1_candidate} 후보가 {region2_rank1_pollrate}%의 득표율로 1위, {region2_rank2_party} {region2_rank2_candidate} 후보가 {region2_rank2_pollrate}%의 득표율로 2위를 달리고 있다.',
}

seq2type = {
	1:'cover', # 표지
	2:'rate', # 투표율 일반
	3:'map', # 투표율 비교
	4:'map', # 투표율 개인화
	5:'rate', # 개표율 일빈
	6:'graph', # 개표율 비교
	7:'map', # 개표율 개인화
	8:'winner', # 득표율 일반
	9:'graph', # 득표율 개인화(선거유형)
	10:'graph', # 득표율 개인화(지역1)
	11:'graph', # 득표율 개인화(지역2)
}
