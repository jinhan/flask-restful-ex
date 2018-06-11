text_templates = {
	# 여러개 선택될 때는 ?
	'1': '{}',

	### 투표율
	'2': '13일 오전 6시를 기해 시작된 제7회 전국동시지방선거가 오후 6시에 모두 마무리되었다. 이번 선거의 전국 최종 투표율은 {toorate_avg_nat}%로 집계되었다.',
	
	'2-1': '제7회 전국동시지방선거가 13일 오전 6시를 기해 전국의 투표소에서 시작되었으며, {hour} 전국 투표율은 {toorate_avg_nat}%로 집계되었다.', # 투표중

	'3': '이는 2014년 6회 지방선거의 최종 투표율 {past_toorate}%보다 {current_toorate_past_toorate}%포인트 {toorate_compare} 수치다. 전국에서 투표율이 가장 높은 지역은 {toorate_rank1}이며, {toorate_rank}{josa} 그 뒤를 이었다.',
	
	'3-1': '이는 2014년 6회 지방선거의 같은 시간대 투표율 {past_toorate}%보다 {current_toorate_past_toorate}%포인트 {toorate_compare} 수치다. 이 시간까지 전국에서 투표율이 가장 높은 지역은 {toorate_rank1}이며, {toorate_rank}{josa} 그 뒤를 따르고 있다.', # 투표중

	'4': '{region1}의 투표율은 {toorate_region1}%로 전국 평균보다 {toorate_region1_toorate_avg_nat}% 포인트 {toorate_compare1} 수치이다.', 

	'4-1': '{region1}의 투표율은 {toorate_region1}%로 전국 평균보다 {toorate_region1_toorate_avg_nat}% 포인트 {toorate_compare1} 수치를 보이고 있다.', # 투표중

	# 후보자 db
	'5': '{candidate} 후보가 속해 있는 {candidate_region}의 최종 투표율은 {candidate_region_toorate}%를 기록했다.',

	'5-1': '{candidate} 후보가 속해 있는 {candidate_region}의 투표율은 {hour} 현재 {candidate_region_toorate}%를 기록하고 있다.', # 투표중

	'6': '문재인 정부 2년차에 치뤄진 이번 선거는, 지난 선거보다 높은 최종투표율을 보이며 국민들의 뜨거운 관심 속에 투표가 마무리 되었다.', # 최종투표율이 지난 선거보다 높을 경우
	'6-0': '문재인 정부 2년차에 치뤄진 이번 선거는, 지난 선거보다 낮은 최종투표율을 보이며 국민들의 저조한 참여 속에 투표가 마무리 되었다.', # 추후 투표율이 낮을 경우도 추가

	'6-1': '전국적으로 지난 선거보다 높은 투표율을 보여 문재인 정부 2년차에 치뤄진 이번 선거에 대한 뜨거운 관심을 확인할 수 있다.', #지난 선거보다 동일시간대 전국투표율이 5% 포인트 이상 높을 경우
	'6-2': '문재인 정부 2년차에 치뤄진 이번 선거에 대한 국민들의 열띤 투표 의지를 확인할 수 있다.',  # 지난 선거보다 동일시간대 투표율이 높은 선거구 수가 전체의 80% 이상일 경우

	'6-3': '전국적으로 지난 선거보다 낮은 투표율을 보이고 있어 각종 이슈에 묻힌 지방선거에 대한 낮은 주목도를 반영하고 있다.', # 지난 선거보다 동일시간대 전국투표율이 5% 포인트 이상 낮을 경우
	'6-4':  '이번 제7회 전국동시지방선거의 투표율은 지난 제6회 지방선거와 유사한 수준으로 나타나고 있다.', # 지난 선거와 동일시간대 전국투표율이 5% 포인트 이내일 경우
		

	### 개표율
	# 지난 선거의 시간대 별 개표율 
	'7': '{hour} 현재 제7회 지방선거 개표가 진행중이며 개표율은 전국 평균 {openrate_avg_nat}%이다.',

	'8': '{hour} 현재 시도지사 선거에서 가장 개표가 빠른 지역은 {openrate_sunname1_rank1}{josa} {openrate_sunname1_rank1_rate}%의 개표율을 보이고 있으며, {openrate_sunname1_rank2}{josa} {openrate_sunname1_rank2_rate}%로 뒤따르고 있다.', # 개표 중

	'8-1':'{hour} 현재 {open_finished}의 시도지사 선거의 개표가 완료되었다. {openrate_sunname1_rank1}{josa1} {openrate_sunname1_rank1_rate}%의 개표율로 그 뒤를 이어 개표가 마무리되고 있다.', # 1개 이상 완료, 몇개 표시? 


	'9': '{hour} 현재 시군구청장 선거에서 {openrate_sunname2_rank1}{josa1} {openrate_sunname2_rank1_rate}%로 개표가 가장 빠르게 이루어지고 있으며, {openrate_sunname2_rank2}{josa2} {openrate_sunname2_rank2_rate}%의 개표율로 그 뒤을 잇고 있다.',

	'9-1': '{hour} 현재 {open_finished} 등의 지역에서 시군구청장 선거의 개표가 완료되었다. 그 다음으로는 {openrate_sunname2_rank1}{josa} {openrate_sunname2_rank1_rate}%의 개표율을 보이며 개표를 마무리짓고 있다.',  # 1개 이상 완료, 몇개 표시?

	'10': '{hour} 현재 {region1}의 개표율은 {openrate_region1}%로 전국 평균보다 약 {openrate_region1_openrate_avg_nat}% 포인트 {compare_region1} 수치이다.', # 개표율 > 0 && 개표율 <100

	'10-1': '{hour} 현재 {region1}{josa1} 아직 개표가 시작되지 않았다.', # 개표율 = 0

	'10-2': '{hour} 현재 {region1}의 개표가 마감되었다.', # 개표율=100

	'11': '전국 {poll_num_sunname}개의 {poll} 선거에서 개표율 1위를 달리고 있는 {poll_openrate_rank1} 지역은 {poll_openrate_rank1_rate}%의 개표율을 보이고 있다. 그 뒤를 {poll_openrate_rank2} 지역이 {poll_openrate_rank1_rate}%로 따르고 있다. {poll} 선거의 전국 평균 개표율은 {poll_openrate_nat_avg}%이다.',

	'11-1': '{hour} 현재 {poll}{josa} 아직 개표가 시작되지 않았다.',

	'11-2': '{hour} 현재 {poll} 선거의 개표는 마감되었다.',

	'12': '{candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거 개표율은 {candidate_poll_openrate}%이다.',

	'12-1': '{candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거는 아직 개표가 시작되지 않았다.',

	'12-2': '{candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거는 개표가 마무리되었다.',

	# 언제 시도, 언제 구시군, 언제 전국 평균
	'13': '{hour} 현재 {open_finished_sido} 지역의 시도지사 선거의 개표가 가장 빠르게 완료되었다.', #{개표율.시도.순위1}=100

	'13-1': ' {hour} 현재 시군구청장 선거에서 {open_finished_gusigun} 지역의 개표가 가장 빠르게 완료되었다.', # {개표율.시군구청장.순위1}=100

	'13-2': '{hour} 현재 모든 지역에서 개표가 완료되었다.', # {개표율.전국.평균}=100
	
	
	### 득표율
	'14': '{hour} 현재 제7회 지방선거 개표가 진행중인 가운데, 전국 17개의 시·도지사 선거에서 {rank1_party}{josa2} {rank1_party_num}개의 선거구에서 1위를 달리고 있다',
	# 동률일때

	'15-3': '{hour} 현재 전국 17개의 시·도지사 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {ranks_party}{josa2} 잇고 있다.', # 선택한 개인화 요소가 시도지사만 있을때(ex. 지역 선택이 없고, 후보나 선거 종류(시도지사)만 골랐을 때

	'15-4': '{hour} 현재 총 226개의 시군구청장을 선출하는 이번 지방선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {ranks_party}{josa2} 잇고 있다.', # 선택한 개인화 요소가 시군구청장만 있을때(ex. 지역 선택이 없고, 후보나 선거 종류(시군구청장)만 골랐을 때

	'15-2': '{hour} 현재 6.13 지방선거와 함께 치러지는 국회의원 재보궐 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {ranks_party}{josa2} 잇고 있다.', # 선택한 개인화 요소가 국회의원만 있을때(ex. 지역 선택이 없고, 후보나 선거 종류(국회의원)만 골랐을 때

	# 무슨 지역?: 득표율 가장 높은 지역
	'15-11': '{hour} 현재 6.13 지방선거와 함께 치러지는 교육감 선거에서 {openrate_rank1_region} 지역의 {openrate_rank1_region_candidate} 후보가 현재 1위를 달리고 있다. 그 뒤를 {openrate_rank2_region_candidate} 후보가 잇고 있다.', # 선택한 개인화 요소가 교육감만 있을때(ex. 지역 선택이 없고, 후보나 선거 종류(교육감)만 골랐을 때
	
	# 득표율 개인화 지역별, 시도지사
	'16': '{hour} 현재 {region1} {region1_poll} 선거에서는 {region1_openrate}%의 개표율을 보이는 가운데 {region1_rank1_party} {region1_rank1_name} 후보가 {region1_rank1_rate}%의 득표율로 1위, {region1_rank2_party} {region1_rank2_name} 후보가 {region1_rank2_rate}%의 득표율로 2위를 달리고 있다.', # 경합, 우세 이외의 상황

	'16-1': '{hour} 현재 {region1} {region1_poll} 선거에서는 {region1_openrate}%의 개표율을 보이는 가운데 {region1_rank1_party} {region1_rank1_name} 후보가 {region1_rank1_rate}%의 득표율로 1위, {region1_rank2_party} {region1_rank2_name} 후보가 {region1_rank2_rate}%의 득표율로 2위를 차지해 경합을 벌이고 있다.',  # 1위와 2위가  5% 이내
	
	'16-2': '{hour} 현재 {region1} {region1_poll} 선거에서는 {region1_openrate}%의 개표율을 보이는 가운데 {region1_rank1_party} {region1_rank1_name} 후보가 {region1_rank1_rate}%의 득표율로 1위, {region1_rank2_party} {region1_rank2_name} 후보가 {region1_rank2_rate}%의 득표율로 2위를 차지해 격차가 벌어지고 있다.', # 1위와 2위가 15% 이상의 격차	
	# 확정이후
	'16-3': '{region1} {region1_poll} 선거에서 {region1_rank1_party} {region1_rank1_name} 후보가 현재 {region1_rank1_rate}%의 득표율을 보이고 있는 가운데 당선이 확정되었으며, {region1_rank2_party} {region1_rank2_name} 후보가 2위를 기록했다.', # 1위와 2위의 격차 > 남은 표수


	'17': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 1위, {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 2위를 달리고 있다.', # 경합, 우세, 열세 이외의 상황, 기본
	# 내가 선택한 후보가 1위일때, 경합
	'17-1': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 1위, {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 2위를 기록하며 {candidate_poll_rank1_name} 후보가 근소한 차이로 앞서면서 경합을 벌이고 있다.', # 경합
	# 내가 선택한 후보가 2위일때, 경합
	'17-2': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 1위, {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 2위를 기록하며 {candidate_poll_rank2_name} 후보가 근소한 차이로 1위 후보를 추격하면서 경합을 벌이고 있다. ',

	'17-3': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 1위를 기록하고 있으며, {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 2위를 기록하고 있다. ', # 내가 선택한 후보가 1위일때, 1위와 2위의 격차가 15% 이상

	'17-4': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 2위를 기록하고 있으며, {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 앞서 있다. ', # 내가 선택한 후보가 2위일때, 1위와 2위의 격차가 15% 이상
	
	# TODO:
	'17-5': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 1위, {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 2위를 기록하며 경합을 벌이고 있으며, {candidate} 후보의 경우 뒤쳐진 {candidate_poll_rank1_rate}%의 득표율을 보이고 있다.', # 내가 선택한 후보가 3위 이하일때, 1위와 2위가 5% 이내

	'17-6': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 당선이 확정되었다.', # 내가 선택한 후보가 1위일때, 1위와 2위의 격차 > 남은 표수

	'17-7': '{hour} 현재 {candidate} 후보가 속해 있는 {candidate_region}의 {candidate_poll} 선거에서는 {candidate_poll_rank2_name} 후보가 {candidate_poll_rank2_rate}%의 득표율로 당선에 실패했으며, {candidate_poll_rank1_name} 후보가 {candidate_poll_rank1_rate}%의 득표율로 당선이 확정되었다. ', # 내가 선택한 후보가 2위 이하일때, 1위와 2위의 격차 > 남은 표수

	## 선거구수.관심정당1.시도지사.1위, 관심정당1.시도지사.순위 
	'18': '{party}은 시도지사 선거에서 총 17개 선거구 중 {my_party_rank1_sido_num}개의 선거구에서 득표율 1위를 달리고 있다. 시군구청장 선거에서는 총 226개 선거구 중 {my_party_rank1_gusigun_num}개의 선거구에서 득표율 1위를 달리고 있다.', # 경합, 우세, 열세 이외의 상황

	'18-1': '현재 시도지사 선거에서 {party_rank1_sido_name}{josa1} {party_rank2_sido_name}{과|와} 경합 중이다. {party_rank1_sido_name}{josa1} 현재 {party_rank1_sido_num}개의 시도지사 선거에서, {party_rank1_gusigun_num}개의 시군구청장 선거에서 1위를 달리고 있다.',   #1,2위 경합

	'18-2': '현재 시도지사 선거에서 {party_rank1_sido_name}{josa} 한 발 앞서 1위를 달리고 있는 가운데 {party_rank2_sido_name}{josa1} {party_rank3_sido_name}{과|와} 비슷한 득표율을 보이고 있다. {party_rank1_sido_name}{josa1} 현재 {party_rank1_sido_num}개의 시도지사 선거에서, {party_rank1_gusigun_num}개의 시군구청장 선거에서 1위를 달리고 있다.', # 2,3위 경합

	'18-3': '현재 시도지사 선거에서 {party_rank1_sido_name}, {party_rank2_sido_name}, {party_rank3_sido_name} 모두가 비슷한 전체 선거구 대비 정당 점유율을 보이고 있다. {party_rank1_sido_name}{josa1} 현재 {party_rank1_sido_num}개의 시도지사 선거에서, {party_rank1_gusigun_num}개의 시군구청장 선거에서 1위를 달리고 있다.', # 1,2,3위 경합

	'18-4': '현재 시도지사 선거에서 {party_rank1_sido_name}이 압도적인 정당 점유율 1위를 보이고 있다. {party_rank1_sido_name}은 현재 {party_rank1_sido_num}개의 선거구에서 우세를 보이며 {party_rank2_sido_name}과의 격차를 벌리고 있다. 시군구청장 선거에서는 {party_rank123_gusigun_name} 순서로 정당 점유율 우세를 보이고 있다. ', # 내가 선택한 정당이 1위일때, 1위와 2위의 격차가 15% 이상

	'18-5': '현재 시도지사 선거에서 {party_rank1_sido_name}이 {party_rank1_sido_name}과의 경쟁에서 열세를 보이고 있다. {party_rank1_sido_name}{josa1} {party_rank1_sido_num}개의 선거구에서 우세를 보이며 1위를 추격중이다. 시군구청장 선거에서는 {party_rank123_gusigun_name} 순서로 정당 점유율 우세를 보이고 있다. ', # 내가 선택한 정당이 2위일때, 1위와 2위의 격차가 15% 이상

	'18-6': '{party}은 시도지사 선거에서 총 17개 선거구 중 {party_rank1_sido_num_confirm}명의 후보의 당선이 확정되었으며, 시군구청장 선거에서는 총 226개의 선거구 중 {party_rank1_gusigun_num_confirm}명의 후보의 당선이 결정지어 이번 지방 선거에서 우세를 점했다.', 

	'18-7': '{party}은 시도지사선거에서 총 17개 선거구 중 {party_rank1_sido_num_confirm}명의 후보의 당선이 확정되었으며, 시군구청장 선거에서는 총 226개의 선거구 중 {party_rank1_gusigun_num_confirm}명의 후보의 당선을 결정지어 이번 지방 선거에서 다소 밀리는 모습을 보였다.',

	# 선거 선택
	'19': '{hour} 현재 6.13 지방선거와 함께 치러지는 국회의원 재보궐 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}{josa2} 잇고 있다.', # 경합, 우세 이외의 상황, 국회의원 보궐선거 선택

	'19-1': '{hour} 현재 전국 시도지사 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있으며, 그 뒤를 {rank2_party}{josa2} 쫓고 있다.', # 경합, 우세 이외의 상황, 시도지사 선거 선택

	'19-2': '{hour} 현재 전국 시군구청장 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있으며, 그 뒤를 {rank2_party}{josa2} 쫓고 있다.',  # 경합, 우세 이외의 상황, 시군구청장 선거 선택

	'19-4': '{hour} 현재 6.13 지방선거와 함께 치러지는 국회의원 재보궐 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있다. 그 뒤를 {rank2_party}{josa2} 바짝 쫓으며 경합을 벌이고 있다.', # 현재 1위인 선거구의 수가 가장 많은 정당과 그 다음인 정당의 차이가 전체 선거구의 5% 이내, 국회의원 보궐선거 선택

	'19-5': '{hour} 현재 전국 시도지사 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있으며, 그 뒤를 {rank2_party}{josa2} {rank2_party_num}개의 선거구에서 1위로 바짝 쫓고 있다.', #현재 1위인 선거구의 수가 가장 많은 정당과 그 다음인 정당의 차이가 전체 선거구의 5% 이내, 시도지사 선거 선택

	'19-6': '{hour} 현재 전국 시군구청장 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있으며, 그 뒤를 {rank2_party}{josa2} 바짝 쫓고 있다.', # 현재 1위인 선거구의 수가 가장 많은 정당과 그 다음인 정당의 차이가 전체 선거구의 5% 이내, 시군구청장 선택

	'19-7': '{hour} 현재 6.13 지방선거와 함께 치러지는 국회의원 재보궐 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리며 우위를 점하고 있다. 그 뒤를 {rank2_party}{josa2} 잇고 있다.', # 현재 1위인 선거구의 수가 가장 많은 정당과 그 다음인 정당의 차이가 전체 선거구의 15% 이상, 국회의원 보궐선거 선택

	'19-8': '{hour} 현재 전국 시도지사 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있으며, {rank2_party}{josa2} {rank2_party_num}개의 선거구에서 1위로 한발 뒤쳐져 있는 상태이다.', # 현재 1위인 선거구의 수가 가장 많은 정당과 그 다음인 정당의 차이가 전체 선거구의 15% 이상, 시도지사 선거 선택

	'19-9': '{hour} 현재 전국 시군구청장 선거에서 {rank1_party}{josa1} {rank1_party_num}개의 선거구에서 1위를 달리고 있으며, 그 뒤를 {rank2_party}{josa2} {rank2_party_num}개의 선거구에서 1위를 기록하며 추격하고 있다.', # 현재 1위인 선거구의 수가 가장 많은 정당과 그 다음인 정당의 차이가 전체 선거구의 15% 이상, 시군구청장 선택

	'19-14': '{hour} 현재 6.13 지방선거와 함께 치러지는 국회의원 재보궐 선거에서 {confirms_rank1_party}{josa3} {confirms_rank1_party_num}개의 국회의석을 차지했다. {confirms_rank2}', # 당선 확정 선거구의 수가 가장 많은 정당과 그 다음인 정당의 격차 > 남은 선거구 수, 국회의원 보궐선거 선택

	'19-15': '{hour} 현재 전국 시도지사 선거에서 {confirms_rank1_party}{josa3} {confirms_rank1_party_num}개의 시장과 도지사의 자리를 차지했다. {confirms_rank2}', # 당선 확정 선거구의 수가 가장 많은 정당과 그 다음인 정당의 격차 > 남은 선거구 수, 시도자시 선거 선택

	'19-16': '{hour} 현재 전국 시군구청장 선거에서 {confirms_rank1_party}{josa3} {confirms_rank1_party_num}개의 시장과 도지사의 자리를 차지했다. {confirms_rank2}', # 당선 확정 선거구의 수가 가장 많은 정당과 그 다음인 정당의 격차 > 남은 선거구 수, 시군구청장선거 선택

	'19-3': '{hour} 현재 전국 교육감 선거에서 개표가 가장 빠른 {open_rank1_region} 지역의 {open_rank1_region_candidate} 후보가 현재 1위를 달리고 있다. {open_rank2}', # 경합, 우세 이외의 상황, 교육감 선거 선택

	'19-17': '{hour} 현재 전국 교육감 선거에서 {confirms_open_rank1_region}에서 {confirms_open_rank1_region_candidate} 후보가 당선이 확정되었다. {confirms_open_ranks}', # 교육감 선거 선택, 당선 확정 지역이 나왔을 경우(가장 먼저 당선 확정된 지역 먼저)

	# 20: '득표율 특이사항',
	'20-1': '{region} 의 {poll} 선거에서 현재 {poll}인 {current_name} 후보가 탈락의 고배를 마셨다. {current_name} 후보는 {rank1_name} 후보에게 {diff_percent}% 포인트 차이로 패하며 연임에 실패했다.',

	'20-2': '{region} 의 {poll} 선거에서 현재 {poll}인 {current_name} 후보가 재선에 성공했다. {current_name} 후보는 {rank2_name} 후보에게 {diff_percent}% 포인트 차이로 승리하며 연임에 성공했다.',

	'20-3': '이번 선거에서 과연 지역주의 구도가 타파될지도 관심사이다. 현재 호남지역 시군구청장 선거에서 자유한국당이 {bs_jayu}개의 선거구에서 1위를 달리고 있으며, 같은 보수 정당인 바른미래당은 {bs_bamin}개의 선거구에서 1위를 달리고 있다. 보수정당들은 현재 호남지역의 {bs_ratio}%의 선거구에서 1위를 달리고 있다.',

	'20-4': '이번 선거에서 과연 지역주의 구도가 타파될지도 관심사이다. 현재 대구경북지역 시군구청장 선거에서 더불어 민주당이 {jb_minju}개의 선거구에서 1위를 달리고 있으며, 진보 정당인 정의당은 {jb_jung}개의 선거구에서 1위를 달리고 있다. 진보 정당들은 현재 대구경북지역의 {jb_ratio}%의 선거구에서 1위를 달리고 있다.',

	'20-5': '제 7회 지방선거에 단독 정당을 처음으로 출정한 바른미래당은 {hour} 현재, 시도지사 선거에서는 {sido_rank1_party_num}개, 시군구청장 선거에서는 {gusigun_rank1_party_num}개의 선거구에서 1위를 달리고 있다. 과연 충분한 성과를 얻어 원내 3당의 입지를 확고히 할 수 있을지 귀추가 주목된다.',

	# TODO: 20-5 추가됨
	'20-6': '지난 제6회 지방선거에서 새정치민주연합은 시도지사 8석, 시군구청장 80석, 새누리당은 시도지사 7석, 시군구청장 117석을 차지했었다. 이번 선거에서는 더불어 민주당이 {minju_num}개의 시도지사 선거에서 1위를 달리고 있으며 자유한국당은 {jayu_num}개의 시도지사 선거에서 1위를 달리고 있다.',

# 	21: '{hour} 현재 모든 선거구에서의 개표가 완료되고 총 17명의 시도지사, 226명의 구시군의장, 824명의 광역의원, 2927명의 지역의원의 당선이 확정되었다. 또한 17명의 교육감과 5명의 교육의원의 당선이 확정되었다.',
# 	'{현재 시간.시각} 현재 
# [{선거명.관심후보1.당선확정} 선거에서 {후보명.관심후보1.당선확정} 후보가,]
# [{관심지역1}{시장|도지사} 선거에서 {후보명.관심지역1.시도지사.당선확정} 후보가,]
# [{관심지역1}{시장|구청장|군수} 선거에서 {후보명.관심지역1.시군구청장.당선확정} 후보가,]
# 당선이 확정되었습니다.'

	'22': '역대 지방선거 투표율 중 가장 높았던 1995년 제1회 지방선거의 투표율인 68.4%에 비하면 제7회 지방선거의 투표율은 {toorate_avg_nat}%로 부족하지만 국민들의 관심과 참여로 이루어진 선거인 만큼 향후 4년간 발전하는 정치를 기대해 본다.', # compare

	'22-20': '제7회 지방선거의 투표율은 {toorate_avg_nat}로 역대 지방선거 투표율 중 가장 높았던 1995년 제1회 지방선거의 투표율인 68.4%를 넘어 국민들의 이번 선거에 대한 뜨거운 관심을 보여주고 있다.', #compare
	
	'22-22': '투표 전 실시된 북미회담과 지방선거 다음날 치러질 러시아 월드컵 등 다양한 글로벌 이슈로 인해 지방선거 투표율이 영향을 받았다는 견해도 있다. 지난 2014년 지방선거와 2010년 지방선거 역시 중앙발 이슈였던 세월호 사고와 천안함 폭침 사건 등으로 대전의 경우 투표율이 전국 평균에 못 미치는 50%대 초반 수준에 머물렀다.', 

	'22-1': '이번선거를 통해 총 17명의 시도지사, 824명의 시도의회의원, 2927명의 구시군의회의원, 17명의 교육감, 5명의 교육의원의 당선이 확정될 예정이다.', # text

	'22-2': '이번 지방선거의 최종 경쟁률은 2.3:1로 경쟁률이 가장 높았던 제 4회 지방선거 3.2:1에 비하면 낮게 나타났다. 17개 시도지사 선거에는 71명이 등록해 4.2:1, 226명을 선출하는 시군구청장 선거에는 756명이 출마해 3.3:1의 경쟁률을 보였다.',

	'22-3': '이번 지방선거에는 총 426억여원의 보조금이 지급되었다. 정당별로 배분된 선거보조금은 자유한국당이 137억 6430만원, 더불어민주당이 135억 3834만원, 바른미래당이 98억 8386만원, 정의당과 민주평화당이 각각 27억 1033만원과 25억 4930만원이다. 선거 보조금 총액은 선거권자 총수를 기준으로 결정되며, 선거 보조금 배분은 지난 총선에서 각 정당이 얻은 득표율을 기준으로 한다.',

	'22-4': '오후 6시 투표를 마감한 결과, 전국 {yoo}명의 유권자 중 {too}명이 투표에 참여한 것으로 잠정 집계됐다. 이번 지방선거를 통해 당선된 당선자들의 임기는 총 4년(2018.7.1.~2022.6.30.)이다.',

	'22-5': '투표 마감 결과, 가장 투표율이 높은 지역은 시도 단위에서는 {sido_rank1}{josa1}, 시군구 단위에서는 {gusigun_rank1}{josa2} 나타났다.',
	
	'22-6': '제7회 지방선거에서 선거인수가 가장 많은 곳은 {rank1}{josa1} 총 {rank1_num}명이 이번 지방선거 선거인 명부에 등재되었다. 해당 지역의 투표율은 {toorate}% 이다.',

	'22-7': '제7회 지방선거에서 선거인수가 가장 적은 곳은 {rank1}{josa1} 총 {rank1_num}명이 이번 지방선거 선거인 명부에 등재되었다. 해당 지역의 투표율은 {toorate}% 이다.',


	'23-0': '제7회 전국동시지방선거를 마무리하며 다시 한 번 초심을 잃지 않는 국민을 위한 올바른 정치를 기대해본다.',

	'23-1': '선거를 전후로 다양한 정치적 이슈들이 논란이 된 만큼 국민들의 다양한 의사와 염원이 반영된 정치를 기대해본다.', #  투표완료후

	'23-2': '다양한 정치적 이슈들이 논란이 되고 있는 만큼 당선자들의 초기 행보에 대한 국민들의 기대가 클 것으로 예상된다.',

	'23-3': '이번 지방선거의 결과가 단순히 후보자를 선발하는 것에 그치지 않고 이를 통해 표출된 국민들의 민심과 정치적 견해를 충분히 반영한 발전하는 정치를 기대해 본다.',

	'23-4': '{hour} 제7회 전국동시지방선거가 최종적으로 종료되었다.',

	'23-5': '수많은 대형 이슈들에 의해 상대적으로 관심을 받지 못했던 제7회 지방선거가 높은 투표율로 국민 참여의 장이 될 수 있을지 그 결과가 주목된다.',
	'23-6': '높은 사전 투표율을 보였던 이번 선거가 과연 얼마나 높은 투표율을 보일 수 있을지 기대해본다.',
	'23-7': '개표가 시작된 가운데 과연 어떤 결과가 나타날 것인지 국민들의 이목이 집중되고 있다.', 
	'23-8': '개표가 시작된 가운데 후보들은 각자의 캠프에서 묵묵히 선거의 결과를 기다리고 있다.',
	'23-9': '개표가 계속 진행되는 가운데 일부 지역에서는 벌써부터 큰 차이를 두고 우위를 달리는 후보들에 대한 관심이 집중되고 있다. ',
	'23-10': '개표가 계속 진행되는 가운데 예상할 수 없는 결과를 앞두고 선거 결과에 관심이 쏠리고 있다.',
	'23-11': '제7회 전국동시지방 선거가 마무리 되어가고 있다. 이번 선거의 결과가 국민들에게 행복을 줄 수 있기를 희망해본다.',
	'23-12': '제7회 전국동시지방선거가 끝을 향해 달려가는 가운데, 국민의 뜻에 따른 바른 정치를 기대해본다.',

}

# seq2type = {
# 	1:'cover', # 표지
# 	2:'rate', # 투표율 전체: 투표중, 마감이후
# 	3:'map', # 투표율 비교 / 전국 : 투표중, 마감이후
# 	4:'map', # 투표율 개인화 / 지역 : 투표중, 마감이후 region1
# 	5:'map', # 투표율 개인화 / 후보 : 투표중, 마감이후 candidate_region, 후보가 속해있는 지역의
# 	6:'default', # 투표율 특이사항

# 	7:'rate', # 개표율 전체
# 	8:'map', # 개표율 비교 / 시도지사
# 	9:'graph', # 개표율 비교 / 시군구청장
# 	10:'map', # 개표율 개인화 / 지역: 개표율 > 0, 개표율 = 0
# 	11:'graph', # 개표율 개인화 / 선거: 개표율 > 0, 개표율 = 0
# 	12:'map or default', # 개표율 개인화 / 후보: 개표율 > 0, 개표율 = 0, 5번  처럼 map으로
# 	13:'default', # 개표율 특이사항

# 	14:'winner', # 득표율 전체
# 	15:'winner', # 득표율 시도지사, 시군구청장, 국회의원, 교육감
# 	16:'graph', # 득표율 개인화 / 지역 : 확정이전, 확정이후
# 	17:'graph', # 득표율 개인화 / 후보 : 확정이전, 확정이후
# 	18:'default', # 득표율 개인화 / 정당 : 확정이전, 확정이후 graph
# 	19:'default', # 득표율 개인화 / 선거 : 확정이전, 확정이후 graph
# 	20:'default', # 득표율 특이사항

# 	21:'default', # 당선확정
# 	22:'default', # transition
# 	23:'default', # 마무리
# }
background_variations = {
    '6': 1,
    '6-0': 2,
    '6-1': 3,
    '6-2': 4,
	'6-3': 2,
	'6-4': 3,
    '22-0': 1,
    '22-4': 2,
    '22-5': 3,
    '22-6': 4,
    '22-7': 1,
    '22-22': 5
}