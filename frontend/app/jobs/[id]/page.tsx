import { JobDetailClient } from "./job-detail-client";

export default async function JobDetailPage(props: PageProps<"/jobs/[id]">) {
  const { id } = await props.params;
  return <JobDetailClient id={id} />;
}
