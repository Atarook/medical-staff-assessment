import { useRouter } from 'next/router'
import { ArrowLeft, ArrowRight, ChevronDown, ChevronUp } from 'lucide-react'
import { useEffect } from 'react'
import { addDays, subDays } from 'date-fns'
import { Header } from '@/layout/Header'
import { Page } from '@/layout/Page'
import { useStationsAPI } from '@/api/stations'
import { usePatientsAPI } from '@/api/patients'
import { Sidebar } from '@/layout/Sidebar'
import { formatDate } from '@/util/formatDate'
import { parseDateString } from '@/util/parseDateString'
import { noop } from '@/util/noop'
import { ClassificationCard } from '@/components/ClassificationCard'
import { usePatientClassification } from '@/api/classification'
import { subsetByAttribute } from '@/util/subsetByAttribute'

export const PatientClassification = () => {
  const router = useRouter()
  const id = router.query.id as string
  const patientId = router.query.patientId as string
  const dateString: string = (router.query.date as string | undefined) ?? ''
  const date = parseDateString(dateString)
  const { stations } = useStationsAPI()
  const currentStation = stations.find(value => value.id === id)
  const { patients } = usePatientsAPI(currentStation?.id)
  const currentPatient = patients.find(value => value.id === patientId)
  const { classification } = usePatientClassification(patientId)
  const currentPatientIndex = patients.findIndex(value => value.id === currentPatient?.id)
  const nextPatientIndex = currentPatientIndex !== -1 ? (currentPatientIndex + 1) % patients.length : undefined
  const nextPatient = nextPatientIndex !== undefined ? patients[nextPatientIndex] : undefined

  useEffect(noop, [router.query.date]) // reload once the date can be parsed

  return (
    <Page
      header={(
        <Header
          start={(
            <div className="flex flex-row gap-x-2 items-center">
              <button onClick={() => router.push(`/stations/${id}`)}><ArrowLeft/></button>
              <h2 className="text-2xl bold">{currentPatient?.name}</h2>
            </div>
          )}
          end={(
            <div className="flex flex-row gap-x-4 items-center">
              <div className="flex flex-col gap-y-1">
                <a href={`/stations/${id}/${patientId}/${formatDate(subDays(date, 1))}`}
                   className="arrow"><ChevronUp/></a>
                <a href={`/stations/${id}/${patientId}/${formatDate(addDays(date, 1))}`}
                   className="arrow"><ChevronDown/></a>
              </div>
              <a href={`/stations/${id}/${nextPatient?.id}/${formatDate(date)}`}>
                <button className="flex flex-row gap-x-2 items-center">Nächsten <ArrowRight size={20}/>
                </button>
              </a>
            </div>
          )}
        />
      )}
      sideBar={classification && (
        <Sidebar className="max-w-[250px] px-4 py-2 flex flex-col gap-y-6 w-full">
          <div className="flex flex-col gap-y-1 w-full">
            <h2 className="font-bold text-xl">Tagesdaten</h2>
            <div className="flex flex-col gap-y-2">
              <label className="flex flex-row gap-x-1">
                <input type="checkbox" checked={classification.isDayOfAdmission} readOnly={true}/>
                Tag der Aufnahme
              </label>
              <label className="flex flex-row gap-x-1">
                <input type="checkbox" checked={classification.isDayOfDischarge} readOnly={true}/>
                Tag der Entlassung
              </label>
              <label className="flex flex-row gap-x-1">
                <input type="checkbox" checked={classification.isInIsolation} readOnly={true}/>
                In Isolation
              </label>
            </div>
          </div>

          <div className="flex flex-col gap-y-2 bg-primary/30 rounded-2xl px-3 py-2">
            <h2 className="font-bold text-xl pb-1">Ergebnis</h2>
            <div className="flex flex-row items-center justify-between">
              Kategorie:
              <strong
                className="bg-white rounded-full px-2 py-1">{classification.result.category1}/{classification.result.category2}</strong>
            </div>
            <div className="flex flex-row items-center justify-between">
              Minutenzahl:
              <strong className="bg-white rounded-full px-2 py-1">{classification.result.minutes}min</strong>
            </div>
          </div>
        </Sidebar>
      )}
    >
      <div className="flex flex-col p-8 gap-y-6 w-full h-full overflow-auto">
        {subsetByAttribute(classification.options, value => value.field__short).map((list, index) => (
          <ClassificationCard key={index} options={list}/>
        ))}
      </div>
    </Page>
  )
}

export default PatientClassification