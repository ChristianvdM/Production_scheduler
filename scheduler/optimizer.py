import pandas as pd
                for role in self.role_priority():

                    self.assign_role(
                        date,
                        campus,
                        role,
                        used_people
                    )

                    used_people_global.update(used_people)

        repair_schedule(
            self.schedule,
            self.skills_df,
            self.availability_df,
            self.assignments
        )

        return self.build_result()

    def build_summary(self):

        summary = pd.DataFrame(self.assignments)

        if summary.empty:
            return pd.DataFrame()

        totals = summary.groupby("Person").size().reset_index(
            name="Total Assignments"
        )

        campus_breakdown = summary.pivot_table(
            index="Person",
            columns="Campus",
            values="Role",
            aggfunc="count",
            fill_value=0
        ).reset_index()

        result = totals.merge(
            campus_breakdown,
            on="Person",
            how="left"
        )

        result["Target Assignments"] = self.target_assignments

        result["Fairness Delta"] = (
            result["Total Assignments"] -
            result["Target Assignments"]
        )

        return result.sort_values(
            by="Total Assignments",
            ascending=False
        )

    def build_result(self):

        assignments_df = pd.DataFrame(self.assignments)

        summary_df = self.build_summary()

        return {
            "assignments": assignments_df,
            "summary": summary_df,
            "schedule": self.schedule,
            "target_assignments": self.target_assignments
        }


def generate_schedule(
    skills_df,
    availability_df
):

    scheduler = Scheduler(
        skills_df,
        availability_df
    )

    return scheduler.generate()
